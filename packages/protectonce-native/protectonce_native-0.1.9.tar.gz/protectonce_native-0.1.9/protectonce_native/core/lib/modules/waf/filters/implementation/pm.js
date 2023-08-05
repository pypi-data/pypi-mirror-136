const BaseFilter = require("../base");
const _ = require('lodash');

const AhoCorasick = require("ahocorasick");

class PmFilter extends BaseFilter {
    constructor(filterDef) {
        super(filterDef, "pm")
        this.matcher = new AhoCorasick(_.castArray(filterDef.value));
        // if (this.cache) this.shouldCache = true;
    }

    doCheckCB(data, originalData, findingCb, doneCb) {
        // return doneCb();

        let match = this.matcher.search(data);
        for (let [pos, patterns] of match) {
            for (let pattern of patterns) {
                findingCb({
                    data,
                    originalData,
                    pattern
                });
            }
        }
        doneCb();
    }


    // *doCheck(data, originalData) {
    //     // return
    //     let match = this.matcher.search(data);
    //     for (let [pos, patterns] of match) {
    //         for (let pattern of patterns) {
    //             yield {
    //                 data,
    //                 originalData,
    //                 pattern
    //             }
    //         }
    //     }
    // }
};

module.exports = PmFilter;