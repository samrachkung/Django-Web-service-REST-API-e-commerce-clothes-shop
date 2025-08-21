class DatabaseRouter:
    """
    A router to control all database operations on models
    """
    def db_for_read(self, model, **hints):
        """Suggest the database to read from"""
        return 'default'
    
    def db_for_write(self, model, **hints):
        """Suggest the database for writes"""
        return 'default'
    
    def allow_relation(self, obj1, obj2, **hints):
        """Allow relations between objects"""
        return True
    
    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """Ensure migrations only run on default database"""
        return db == 'default'