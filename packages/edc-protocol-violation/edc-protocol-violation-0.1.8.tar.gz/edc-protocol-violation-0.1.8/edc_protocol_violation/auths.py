from django.conf import settings
from edc_auth.auth_objects import AUDITOR_ROLE, CLINICIAN_ROLE, CLINICIAN_SUPER_ROLE
from edc_auth.site_auths import site_auths
from edc_data_manager.auth_objects import DATA_MANAGER_ROLE

from edc_protocol_violation.auth_objects import (
    PROTOCOL_INCIDENT,
    PROTOCOL_INCIDENT_VIEW,
    PROTOCOL_VIOLATION,
    PROTOCOL_VIOLATION_VIEW,
    protocol_incident_codenames,
    protocol_incident_view_codenames,
    protocol_violation_codenames,
    protocol_violation_view_codenames,
)

incident_type = getattr(settings, "EDC_PROTOCOL_VIOLATION_TYPE", "violation/deviation")

site_auths.add_group(*protocol_violation_codenames, name=PROTOCOL_VIOLATION)
site_auths.add_group(*protocol_violation_view_codenames, name=PROTOCOL_VIOLATION_VIEW)
site_auths.add_group(*protocol_incident_codenames, name=PROTOCOL_INCIDENT)
site_auths.add_group(*protocol_incident_view_codenames, name=PROTOCOL_INCIDENT_VIEW)

if incident_type == "violation/deviation":
    site_auths.update_role(PROTOCOL_VIOLATION, name=CLINICIAN_ROLE)
    site_auths.update_role(PROTOCOL_VIOLATION, name=CLINICIAN_SUPER_ROLE)
    site_auths.update_role(PROTOCOL_VIOLATION, name=DATA_MANAGER_ROLE)
    site_auths.update_role(PROTOCOL_VIOLATION_VIEW, name=AUDITOR_ROLE)
elif incident_type == "incident":
    site_auths.update_role(PROTOCOL_INCIDENT, name=CLINICIAN_ROLE)
    site_auths.update_role(PROTOCOL_INCIDENT, name=CLINICIAN_SUPER_ROLE)
    site_auths.update_role(PROTOCOL_INCIDENT, name=DATA_MANAGER_ROLE)
    site_auths.update_role(PROTOCOL_INCIDENT_VIEW, name=AUDITOR_ROLE)
else:
    raise ValueError(
        "Invalid value for settings.EDC_PROTOCOL_VIOLATION_TYPE. "
        f"Expected `incident` or `violation/deviation`. Got {incident_type}."
    )
