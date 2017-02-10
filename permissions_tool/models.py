from django.db import models


class PermissionsTool(models.Model):
    """
    Dummy model for holding permissions
    """
    class Meta:
        managed = False
        permissions = (
            ('audit_permissions', 'Can audit permissions'),
        )
