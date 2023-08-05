'use strict';

const Rules = require("./rules");
const Flows = require("./flows");
const Manifests = require("./manifests");

class RuleSet {

    constructor() {
        this.Rules = Rules;
        this.Flows = Flows;
        this.Manifests = Manifests;
        this.count = {};
        this.rawRuleset = {};
    }

    generateRuleset(ruleset) {
        this.Manifests.generateManifests(ruleset.manifest);
        this.Rules.generateRules(ruleset.rules);
        this.Flows.generateFlows(ruleset.flows);
        this.count.manifests = this.Manifests.size;
        this.count.rules = this.Rules.size;
        this.count.flows = this.Flows.size;
        this.rawRuleset = ruleset;
    }

    getCount() {
        return this.count;
    }

    getRuleset() {
        return this.rawRuleset;
    }

    clearRuleset() {
        this.Rules.clear();
        this.Manifests.clear();
        this.Flows.clear();
        this.count = {}
    }
}

module.exports = new RuleSet();
