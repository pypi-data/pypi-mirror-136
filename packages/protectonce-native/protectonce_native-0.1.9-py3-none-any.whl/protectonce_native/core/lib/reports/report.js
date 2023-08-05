const { isNull } = require("lodash");

class Report {
    constructor(id, name, severity, ipAddress, message, type, path, blocked) {
        this.id = id;
        this.name = name;
        this.severity = severity;
        this.ip_addresses = [ipAddress]; // TODO: How to get multiple IP addresses?
        this.security_response = message;
        this.date = new Date();
        this.type = type;
        this.request_path = path;
        this.report_type = "incident"; // TODO: What are other types?
        this.blocked = blocked || false;

        // FIXME: Currently it is same as date, may be once APM is integrated this might have different value
        this.date_started = new Date();
        this.request = 200; // TODO: Check what is this
        this.user = ""; // TODO: This will be done once user management is implemented,
        this.duration = 0; // TODO: What does this indicate?
    }
}

const ReportType = {
    'REPORT_TYPE_REPORT': 'report',
    'REPORT_TYPE_ALERT': 'alert',
    'REPORT_TYPE_BLOCK': 'block'
};

class SecurityActivity {
    constructor(id, status, ipAddress, reponse, verb, path, user) {
        this.events = [];
        this.request_id = id;
        this.status_code = status;
        this.ip_addresses = [ipAddress];
        this.security_response = reponse;
        this.date = new Date();
        this.request_verb = verb;
        this.request_path = path;
        this.user = user ? user : '';
        this.duration = 0;
        this.closed = false;
    }

    addEvent(event) {
        this.events.push(event);
    }

    setClosed() {
        this.closed = true;
    }

    isClosed() {
        return this.closed;
    }
}

class Event {
    constructor(category, request_id, blocked, confidence_level, date, date_started, type, duration, security_response) {
        this.category = category,
            this.request_id = request_id,
            this.blocked = blocked,
            this.confidence_level = confidence_level,
            this.date = date,
            this.date_started = date_started,
            this.type = type,
            this.duration = duration,
            this.security_response = security_response
    }
}

module.exports = {
    Report: Report,
    ReportType: ReportType,
    SecurityActivity: SecurityActivity,
    Event: Event
};
