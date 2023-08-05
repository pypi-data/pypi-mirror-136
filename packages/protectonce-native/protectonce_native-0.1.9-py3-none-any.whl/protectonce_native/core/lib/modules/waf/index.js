const DataFrame = require("./dataFrame");
const _ = require('lodash');
const WAFRulesManager = require("../../rules/waf_rules_manager");
const { WAFData } = require('../../runtime/runtime_data');
const { SecurityActivity, Event, Report, ReportType } = require('../../reports/report');
const ReportsCache = require('../../reports/reports_cache');
const ProtectOnceContext = require('../context');
const Logger = require('../../utils/logger');
const deasync_promise = require("deasync-promise");

async function checkHTTPRequest(request) {
    let requestMapList = new Map();
    let findings1;
    if (WAFRulesManager.isInitialised()) {
        _generateRequestMapList(request, requestMapList);
        if (requestMapList.size > 0) {
            let dataFrame = new DataFrame();
            findings1 = await dataFrame.checkAllFlowsPromise(requestMapList);
        }
    }
    return _generateRuntimeData(request, findings1);
}

function _generateRuntimeData(request, finding) {
    let wafData = null;
    if (finding.length > 0) {
        let securityActivity;
        let wafFind = { action: '', arg: '', context: '', message: 'Alert findings in waf request' };
        wafData = new WAFData(wafFind);
        //FIXME: remove hardcoded values after more clarity on the values
        securityActivity = new SecurityActivity(request.poSessionId, "status", request.sourceIP, "200", request.method, request.path, "user");
        finding.forEach(find => {
            const reportType = find.ruleData.status == 'BLOCK' ? ReportType.REPORT_TYPE_BLOCK : ReportType.REPORT_TYPE_ALERT;
            const report = new Report(find.ruleData.rule_internalName, find.ruleData.rulename,
                reportType == ReportType.REPORT_TYPE_BLOCK ? 'critical' : 'minor',
                request.sourceIP, find.data, find.ruleData.rulename, find.pattern, reportType == ReportType.REPORT_TYPE_BLOCK);

            //Added Event for new implementation of Security Activity
            var event = new Event("waf", request.poSessionId, (reportType == ReportType.REPORT_TYPE_BLOCK), find.ruleData.confidence, new Date(),
                new Date(), find.ruleData.rulename, "", "security_response");
            securityActivity.addEvent(event);

            if (reportType == ReportType.REPORT_TYPE_BLOCK) {
                wafFind = { args: find.data, context: find.pattern, action: find.ruleData.status, message: find.ruleData.rulename };
                wafData = new WAFData(wafFind);
                wafData.setSkip();
            }
        });
        if (securityActivity) {
            ReportsCache.cache(securityActivity);
        }
    } return wafData;
}

function _generateRequestMapList(request, requestMapList) {
    //  const reqEntries = new Map(Object.entries(request));
    const manEntries = WAFRulesManager.getManifestEntries();
    var manifestEnt = manEntries.next();
    while (!manifestEnt.done) {
        const manifest = manifestEnt.value[1];
        const key_access = manifest.getkey_access();
        switch (manifest.getinherit_from()) {
            case "server.request.query": {
                const query = request.queryParams;
                if (!_.isEmpty(query)) {
                    requestMapList.set(manifest.getid, _generateMapList(new Map(Object.entries(query)), manifest));
                }
                break;
            }
            case "server.request.path_params": {
                const path = request.path;
                if (!_.isEmpty(path)) {
                    requestMapList.set(manifest.getid, _generateMapList(new Map(Object.entries(path)), manifest));
                }
                break;
            }
            case "server.request.headers.no_cookies": {
                const headers = request.headers;
                if (!_.isEmpty(headers) && _.isEmpty(key_access)) {
                    const headersCopy = _.cloneDeep(headers);
                    delete headersCopy.cookie;
                    requestMapList.set(manifest.getid(), _generateMapList(new Map(Object.entries(headersCopy)), manifest));
                }
                break;
            }
            case "server.request.cookies": {
                const headers = request.headers;
                if (!_.isEmpty(headers) && headers['cookie']) {
                    const cookies = _cookieParser(headers['cookie']);
                    requestMapList.set(manifest.getid(), _generateMapList(new Map(Object.entries(cookies)), manifest));
                }
                break;
            }
            case "server.request.body": {
                const body = request.body;//TODO
                if (!_.isEmpty(body)) {
                    requestMapList.set(manifest.getid(), _generateBodyMapList(body, manifest));
                }
                break;
            }
            default: {


            }
        }
        manifestEnt = manEntries.next();
    }
    return requestMapList;
}

function _cookieParser(cookieString) {
    if (cookieString === "")
        return {};
    let pairs = cookieString.split(";");
    let splittedPairs = pairs.map(cookie => cookie.split("="));
    const cookieObj = splittedPairs.reduce(function (obj, cookie) {
        obj[decodeURIComponent(cookie[0].trim())]
            = decodeURIComponent(cookie[1].trim());
        return obj;
    }, {})
    return cookieObj;
}

function _generateMapList(valuesMap, manifest) {
    let requestList = new Array();
    let valList;
    const id = manifest.getid();
    if (manifest.getrun_on_key() === true)
        valList = valuesMap.keys();
    else
        valList = valuesMap.values();

    let firstVal = valList.next();
    while (!firstVal.done) {
        requestList.push(firstVal.value);
        firstVal = valList.next();
    }
    return requestList;
}


function _generateBodyMapList(valuesMap, manifest) {
    let requestList = new Array();
    let valList;
    const id = manifest.getid();

    //TODO - Not sure if this is needed
    /* if (manifest.getrun_on_key() === true)
         valList = valuesMap.keys();
     else
         valList = valuesMap.values();*/

    requestList.push(valuesMap);
    return requestList;
}

//initialise the ruleset
function initialise(rulset) {
    WAFRulesManager.initialiseWAFRuleSet(rulset);
}

function updateruleset(rulset) {
    WAFRulesManager.updateWAFRuleSet(rulset);
}

function scanHttpHeaders(requestData) {
    try {
        const request = ProtectOnceContext.get(requestData.data.poSessionId);
        Logger.write(Logger.DEBUG && `waf: Scanning http headers: ${requestData.data.poSessionId}, request: ${request}`);
        return deasync_promise(checkHTTPRequest(request));
    } catch (e) {
        Logger.write(Logger.DEBUG && `waf: Failed to scan http data data: ${e}`);
    }

}

function scanHttpBody(requestData) {

    let result = {
        action: 'none'
    };
    try {
        if (!requestData.data.body) {
            return result;
        }
        const requestBody = {
            'body': new Buffer.from(requestData.data.body).toString()
        }
        Logger.write(Logger.DEBUG && `waf: Scanning http body: ${requestData.data.poSessionId}, request: ${requestBody.body}`);
        return deasync_promise(checkHTTPRequest(requestBody));
    } catch (e) {
        Logger.write(Logger.DEBUG && `httpServer: Failed to store session data ${e}`);
    }

    return result;
}

module.exports = {
    initialise: initialise,
    checkHTTPRequest: checkHTTPRequest,
    updateruleset: updateruleset,
    scanHttpHeaders: scanHttpHeaders,
    scanHttpBody: scanHttpBody
}