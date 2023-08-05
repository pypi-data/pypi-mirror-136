const _ = require('lodash');
const { buildFilter } = require("../filters");
const TargetProcessor = require("./base");


class Rule {

    constructor(ruleDef) {
        //  super(context, ruleDef.rule_id); extends TargetProcessor
        this.rule_id = ruleDef.rule_id;
        //added for backend config
        this.internalName = ruleDef.internalName;
        this.name = ruleDef.name;
        this.status = ruleDef.status;
        this.confidence = ruleDef.confidence;
        this.filters = ruleDef.filters.map(filterDef => {
            filterDef.rule_internalName = this.internalName;
            filterDef.rule_name = this.name;
            filterDef.rule_status = this.status;
            filterDef.confidence = this.confidence;
            return buildFilter(filterDef);
        }).filter(f => f);
        //  this.buildTargetMap(this.filters);
        this.shouldCache = false;
    }

    enrichFinding(finding) {
        finding.ruleId = this.id;
    }

    getStatus() {
        return this.status;
    }

    executeFilters(data, findingCb, doneCb) {
        this.filters.forEach(filter => filter.checkTargetCB(data, findingCb, doneCb));
    }
}

class Rules extends Map {
    constructor() {
        super();
    }

    setRule(rule, context) {
        this.set(rule.rule_id, new Rule(rule));
    }

    generateRules(rules) {
        //TODO : Need to know how to pass context
        (rules || []).forEach(rule => { this.setRule(rule); });
    }
}

module.exports = new Rules();