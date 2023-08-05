
module.exports = {
    buildFilter
};

function buildFilter(filterDef) {
    let filterType = filterDef.operator.slice(1);
    try {
        const Filter = require(`./implementation/${filterType}`);
        return new Filter(filterDef)
    } catch (err) {
        console.error(`Error while trying to load filter ${filterType}. [${err}]`)
    }
}