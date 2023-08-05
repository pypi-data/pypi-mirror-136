const _ = require('lodash');
const { Flows } = require('../modules/waf/ruleset');

const RuleSet = require('../modules/waf/ruleset');

class WAFRulesManager {
    constructor() {
        this.RuleSet = RuleSet;
        this.stopOnFirstFinding = false;
        this.shouldCache = false;
        if (!this.cache) {
            this.shouldCache = false;
        }
    }

    initialiseWAFRuleSet(rules) {
        if (!this.isInitialised() && _.isObject(rules)) {
            this.RuleSet.generateRuleset(rules);
        }
    }

    resetWAFRuleSet() {
        this.RuleSet.clearRuleset();
    }

    //TODO : update the ruleset for heartbeat only for the Rules updated. This is to be implemented in backend first
    updateWAFRuleSet(rules) {
        if (this.isInitialised() && _.isObject(rules))
            this.RuleSet.generateRuleset(rules);
    }

    isInitialised() {
        return (this.RuleSet.count.manifests && this.RuleSet.count.flows && this.RuleSet.count.rules);
    }

    get rulesetCount() {
        return this.RuleSet.count;
    }

    checkAllRules(cb, doneCB, values) {
        this.RuleSet.Rules.forEach(rule => this.checkForRuleCB(values, rule.rule_id, cb, doneCB));
    }

    checkForRuleCB(values, ruleid, cb, doneCB) {
        if (this.RuleSet.Rules.get(ruleid).getStatus() != 'disabled')
            this.RuleSet.Rules.get(ruleid).executeFilters(values, cb, doneCB);
    }

    async checkAllRulesPromise(...values) {
        let findings = [];
        return new Promise((resolve, reject) => {
            this.checkAllRules(f => findings.push(f), () => resolve(findings), ...values);
        });
    }

    //check for all Flows
    checkAllFlows(cb, doneCB, values) {
        this.RuleSet.Flows.forEach(flow => {
            if (flow.getStatus() != 'disabled') {
                this.checkForFlow(cb, doneCB, values, flow);
            }
        });
    }

    //check fo specific Flow
    checkForFlow(cb, doneCB, values, flow) {
        flow.steps.forEach(step => step.rules.forEach(ruleId => { this.checkForRuleCB(values, ruleId, cb, doneCB) }));
    }

    getManifestEntries() {
        if (this.RuleSet.Manifests)
            return this.RuleSet.Manifests.entries();
    }

    _generateRequestMapList() {
        const manEntries = WAFRulesManager.getManifestEntries();
        while (!manEntries.done()) {
            manifest = manEntries.next();
        }
    }
}

module.exports = new WAFRulesManager();
