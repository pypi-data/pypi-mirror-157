from django.db.models import UniqueConstraint, Q
from safedelete import models as safedelete_models


class SoftDeleteCascadeMixin(safedelete_models.SafeDeleteModel):
    _safedelete_policy = safedelete_models.SOFT_DELETE_CASCADE
    UNIQUE_FIELDS = []

    @classmethod
    def get_unique_constraint(cls):
        if cls.UNIQUE_FIELDS:
            raise NotImplemented('get_unique_constraint must be implemented')

        if cls.UNIQUE_FIELDS:
            return UniqueConstraint(fields=cls.UNIQUE_FIELDS, condition=Q(deleted__isnull=True),
                                    name='unique_active_{}'.format('_'.join(cls.UNIQUE_FIELDS)))
