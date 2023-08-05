const BaseFilter = require("../base")

class RxFilter extends BaseFilter {
    constructor(filterDef) {
        super(filterDef, "rx");
        let options = this._decodeOptions(filterDef.options);
        this.regex = new RegExp(filterDef.value, options);
        this.pattern = filterDef.value;
    }

    _decodeOptions(optionsDef) {
        let optionString = ""
        if (!optionsDef.case_sensitive) {
            optionString += "i"
        }
        return optionString;
    }

    doCheckCB(data, originalData, findingCb, doneCb) {
        // return
        let match = data.match(this.regex);
        if (match) {
            const ruleData = this.getRuleDetails();
            findingCb({
                data,
                originalData,
                pattern: this.pattern,
                ruleData: ruleData
            });
        }
        doneCb();
    }

    // *doCheck(data, originalData) {
    //     // return
    //     let match = data.match(this.regex); //TODO: Should this be matchall?
    //     // console.log(JSON.stringify(data), JSON.stringify(this.pattern), match)
    //     if (match) {
    //         yield {
    //             data,
    //             originalData, 
    //             pattern: this.pattern
    //         }
    //     }
    // }

};

module.exports = RxFilter;