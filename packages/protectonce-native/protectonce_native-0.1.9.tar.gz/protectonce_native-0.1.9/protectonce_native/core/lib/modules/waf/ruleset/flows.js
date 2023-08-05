const _ = require('lodash');
const TargetProcessor = require("./base");
const { ACTIONS } = require("../common");

const Logger = require('../../../utils/logger');

class Step {
    constructor(stepDef) {
        //  super(`${flowId}.${stepDef.id}`);
        this.rules = stepDef.rule_ids;//TOD : Will decide to add Rule array here
        // this.buildTargetMap(this.rules); extends TargetProcessor 
        [this.action, this.continue] = this._decodeOnMatch(stepDef.on_match);
        this.stopOnFirstFinding = !this.continue;
        this.shouldCache = false;
    }

    _decodeOnMatch(on_match) {
        return {
            exit_block: [ACTIONS.BLOCK, false],
            exit_monitor: [ACTIONS.REPORT, false]
        }[on_match];
    }

    findingsDone() {
        if (!this.continue) {
            throw new TargetProcessor.StopProcessing(); // don't process the rest of the steps in this flow
        }
    }

    enrichFinding(finding) {
        finding.stepId = this.id;
        finding.action = this.action;
    }
}

class Flow {
    constructor(flowDef) {
        // super(context, flowDef.name);
        this.name = flowDef.name;
        this.internalName = flowDef.internalName;
        this.status = flowDef.status;
        this.steps = flowDef.steps.map(stepDef => new Step(stepDef));
        // this.buildTargetMap(this.steps) extends TargetProcessor
        this.shouldCache = false;
    }

    enrichFinding(finding) {
        finding.flowName = this.id;
    }

    getInternalName() {
        return this.internalName;
    }

    getStatus() {
        return this.status;
    }
}

class Flows extends Map {
    constructor() {
        super();
    }

    setFlow(flow) {
        this.set(flow.name, new Flow(flow));
    }

    generateFlows(flows) {
        Logger.write(Logger.DEBUG && `flows: ${JSON.stringify(flows)}`);
        (flows || []).forEach(flow => { this.setFlow(flow); });
    }
}

module.exports = new Flows();
