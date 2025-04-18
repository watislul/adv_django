class DatabaseRouter:
    """
    A router to control database operations for different apps.
    """
    def db_for_read(self, model, **hints):
        """
        Determine which database to use for read operations.
        """
        if model._meta.app_label == 'resumes':
            return 'mongodb'
        elif model._meta.app_label == 'jobs':
            return 'default'
        elif model._meta.app_label == 'users':
            return 'default'
        return 'logs'

    def db_for_write(self, model, **hints):
        """
        Determine which database to use for write operations.
        """
        if model._meta.app_label == 'resumes':
            return 'mongodb'
        elif model._meta.app_label == 'jobs':
            return 'default'
        elif model._meta.app_label == 'users':
            return 'default'
        return 'logs'

    def allow_relation(self, obj1, obj2, **hints):
        """
        Allow relations if both objects are in the same database.
        """
        if obj1._meta.app_label == obj2._meta.app_label:
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Make sure the appropriate apps migrate to the right databases.
        """
        if app_label == 'resumes':
            return db == 'mongodb'
        elif app_label == 'jobs':
            return db == 'default'
        elif app_label == 'users':
            return db == 'default'
        return db == 'logs'
