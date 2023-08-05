const Logger = require('../../../utils/logger');

class Manifests extends Map {

    constructor() {
        super();
    }

    setManifest(manifest) {
        const id = Object.keys(manifest)[0];
        this.set(id, new Manifest(id, manifest));
    }

    generateManifests(manifestset) {
        Logger.write(Logger.DEBUG && `manifest: ${JSON.stringify(manifestset)}`);
        var manifest_map = new Map(Object.entries(manifestset));
        for (const id of manifest_map.keys()) {
            Logger.write(Logger.DEBUG && `manifest id: ${JSON.stringify(id)}`);
            var manifest = new Manifest(id, manifest_map.get(id));
            this.set(id, new Manifest(id, manifest));
        }
    }

    getManifest(id) {
        this.get(id);
    }

    getRawManifest(id) {
        return this.get(id).rawManifest();
    }
    get rawManifestset() {
        return this.manifestset;
    }
}

//TODO: need to think how to make if more generic for all the possible manifest key:value eg
class Manifest {
    constructor(id, manifest) {
        this.id = id;
        this.inherit_from = manifest.inherit_from;
        this.run_on_key = manifest.run_on_key;
        this.run_on_value = manifest.run_on_value;
        this.manifest = manifest;
        this.key_access = manifest.key_access
    }

    getid() {
        return this.id;
    }

    getinherit_from() {
        return this.inherit_from;
    }

    getrawManifest() {
        return this.manifest;
    }

    getrun_on_key() {
        return this.run_on_key;
    }

    getrun_on_value() {
        return this.run_on_value;
    }

    getkey_access() {
        return this.key_access;
    }
}

module.exports = new Manifests();