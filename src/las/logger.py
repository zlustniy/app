import logging

from las.models import User
from las.services.tools.subject_accumulation import SubjectAccumulationEntity


class LoggerMixin:
    logger_name = None
    log_prefix = None

    def get_extra_prefix(self):
        subject_accumulation = getattr(self, 'subject_accumulation', None)
        match subject_accumulation:
            case SubjectAccumulationEntity():
                return subject_accumulation.log_representation()
        return ''

    def _get_pattern(self, prefix):
        if prefix is None:
            prefix = self.log_prefix
        pattern = f'user=`%s` (id=`%s`) instance=`%s` (id=`%s`) {self.get_extra_prefix()}: `%s`'
        if prefix is not None:
            pattern = f'{prefix}: ' + pattern
        return pattern

    @property
    def logger(self):
        return logging.getLogger(self.logger_name)

    def info(self, user: User, msg: str, prefix=None):
        pattern = self._get_pattern(prefix=prefix)
        self.logger.info(pattern, user.username, user.id, user.instance.name, user.instance.id, msg)

    def debug(self, user: User, msg: str, prefix=None):
        pattern = self._get_pattern(prefix=prefix)
        self.logger.debug(pattern, user.username, user.id, user.instance.name, user.instance.id, msg)

    def exception(self, user: User, msg: str, prefix=None):
        pattern = self._get_pattern(prefix=prefix)
        self.logger.debug(pattern, user.username, user.id, user.instance.name, user.instance.id, msg)

    def log(self, msg: str, level='debug'):
        log_method = getattr(self, level, None)
        log_method(
            user=self.user,
            msg=msg,
        )
