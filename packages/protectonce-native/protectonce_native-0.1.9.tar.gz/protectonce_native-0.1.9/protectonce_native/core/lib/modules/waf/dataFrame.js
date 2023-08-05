const _ = require('lodash');
const { hashStr, StrHash } = require("./common");
const WAFRulesManager = require("../../rules/waf_rules_manager");

const resultsCache = require("./cache");

class ValueList {
    constructor() {
        this.values = [];
        this.cache = {};
        // this._hash = new StrHash();
    }

    add(value) {
        // let newHash = hashStr(String(value));
        this.values.push(value);
        // this._hash.combine(new StrHash(value));
    }

    // get hash() {
    //     return this._hash.valueOf();
    // }

    getTransformedValuesCB(transformerChain, includeTransient, cb, doneCb) {
        return transformerChain(this.values, cb, doneCb, this.cache, includeTransient);
    }

    // *getTransformedValues(transformerChain, includeTransient) {
    //     if (!transformerChain) {
    //         yield *this.values.map((v)=>[v,v]);
    //     } else {
    //         yield *transformerChain(this.values, this.cache, includeTransient);
    //     }
    // }
}

class DataFrame {
    constructor() {
        this.WAFRulesManager = WAFRulesManager;
    }

    // *addAndCheck(targetName, ...values) {
    //     let valueList = this.dataMap[targetName] = (this.dataMap[targetName] || new ValueList());
    //     values.forEach(v=>valueList.add(v));

    //     if (this.ruleset) {
    //         yield* this.ruleset.checkTarget(targetName, valueList); 
    //     }
    // }

    addAndCheckCB(cb, doneCB, values) {
        let valueList = new ValueList();
        values.forEach(v => valueList.add(v)); // TODO: can the be made faster using some sort of extend?

        if (this.ruleset) {
            this.ruleset.checkTargetCB(targetName, valueList, cb, doneCB);
        }
    }

    async addAndCheckPromise(targetName, ...values) {
        let findings = [];
        return new Promise((resolve, reject) => {
            this.addAndCheckCB(targetName, f => findings.push(f), () => resolve(findings), ...values);
        });
    }

    checkAllRules(cb, doneCB, valuesMap) {
        const values = valuesMap.entries();
        var val = values.next();
        while (!val.done) {
            let valueList = new ValueList();
            val.value[1].forEach(v => valueList.add(v));
            this.WAFRulesManager.checkAllRules(cb, doneCB, valueList);
            val = values.next();
        }
    }

    checkAllFlows(cb, doneCB, valuesMap) {
        const values = valuesMap.entries();
        var val = values.next();
        while (!val.done) {
            let valueList = new ValueList();
            val.value[1].forEach(v => valueList.add(v));
            this.WAFRulesManager.checkAllFlows(cb, doneCB, valueList);
            val = values.next();
        }
    }

    async checkAllFlowsPromise(values) {
        let findings = [];
        return new Promise((resolve, reject) => {
            this.checkAllFlows(f => findings.push(f), () => resolve(findings), values);
        });
    }

    async checkAllRulesPromise(values) {
        let findings = [];
        return new Promise((resolve, reject) => {
            this.checkAllRules(f => findings.push(f), () => resolve(findings), values);
        });
    }
}

module.exports = DataFrame;