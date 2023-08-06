from django.db.models import UniqueConstraint, Q
from safedelete import models as safedelete_models


class SoftDeleteCascadeMixin(safedelete_models.SafeDeleteModel):
    class Meta:
        abstract = True

    _safedelete_policy = safedelete_models.SOFT_DELETE_CASCADE

    @staticmethod
    def get_unique_constraint(fields):
        return UniqueConstraint(fields=cls.UNIQUE_FIELDS, condition=Q(deleted__isnull=True),
                                name='unique_active_{}'.format('_'.join(fields)))
