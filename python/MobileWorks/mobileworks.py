import urllib2, json, base64


class _API:
    """
    This is the base class for Task/Job.
    It contains the general methods for making API calls to MobileWorks
    """
    
    class Request( urllib2.Request ):
        """
        This class is an extension of urllib2.Request that allows requests other than GET/POST.
        """
        
        def __init__( self, url, data = None, headers = {},
                     origin_req_host = None, unverifiable = False, method = None ):
            """
            These parameters (except `method`) are the same as the parameters in the parent class `urllib2.Request`, which can be found here:
            http://docs.python.org/library/urllib2.html#urllib2.Request
            
            The `method` parameter was added to allow HTTP requests other than GET/POST.
            """
            self._method = method
            urllib2.Request.__init__( self, url, data, headers, origin_req_host, unverifiable )
        
        def get_method( self ):
            return self._method if self._method else urllib2.Request.get_method( self )
        
    @classmethod
    def _make_request( cls, url, method = None, post_data = None ):
        """
        Creates and sends an HTTP request.
        """
        if MobileWorks.credentials is None:
            raise Exception( 'You are not logged in.' )
        req = cls.Request( url, method = method, data = post_data, headers = {'Content-Type':'application/json'} )
        req.add_header( 'Authorization', 'Basic ' + MobileWorks.credentials )
        
        try:
            response = urllib2.urlopen( req )
            headers = response.info().dict
            content = response.read()
            response.close()
            return headers, content
#            return json.loads( content )
        except urllib2.HTTPError, e:
            if e.code >= 500:
                raise Exception( 'HTTP %d: A server error occured' % e.code )
            else:
                raise Exception( 'HTTP %d: %s' % ( e.code, e.read() ) )
    
    VERSION = 2
    location = None
    
    def url( self ):
        return MobileWorks.DOMAIN + self._path()
    
    def dict( self ):
        """
        This is used for json serialization.
        It should be overriden by subclasses.
        """
        return self.__dict__
    
    def to_json(self):
        return json.dumps( self.dict() )
    
    def post( self ):
        """
        Posts the object to MobileWorks API and returns the URL of the created object.
        """
        headers, content = self._make_request( self.url(), 'POST', self.to_json() )
        if self.VERSION == 1:
            self.location = headers['location']
        elif self.VERSION == 2:
            self.location = json.loads(content)['Location']
        return self.location
    
    @classmethod
    def _retrieve( cls, url ):
        """
        Gets the information of the object located at `url`.
        """
        headers, content = cls._make_request( url )
        return json.loads( content )
    
    def delete( self ):
        """
        Deletes the object located at `url`.
        """
        if self.location is None:
            raise Exception( "This object doen't point to any resource on the server." )
        headers, content = self._make_request( url, 'DELETE' )
        if cls.VERSION == 1:
            return True
        elif cls.VERSION == 2:
            return json.loads( content )
    

class Task(_API):
    
    def __init__( self, location = None, **task_params ):
        if location is not None and task_params:
            raise Exception( "You can't provide a location and task parameters at the same time" )
        if location is not None:
            self.location = location
            self._load()
        else:
            self.params = task_params
            self.fields = None
        
    def _load( self ):
        self.params = Task._retrieve( self.location )
        if 'fields' in self.params:
            self.fields = self.params['fields']
            del self.params['fields']
        else:
            self.fields = None
            
    def _path( self ):
        """
        Returns the base path of tasks depending on the API version.
        """
        if self.VERSION == 1:
            return 'api/v1/tasks/'
        elif self.VERSION == 2:
            return 'api/v2/task/'
        raise Exception( 'Sorry, version %d is not supported by the library yet!' % self.VERSION )
        
    def get_param( self, name ):
        """
        Gets the specified parameter from this task.
        """
        return self.params[name]
        
    def set_params( self, **params ):
        """
        Sets parameters of this task.
        """
        self.params.update( params )
    
    def add_field( self, name, type, **kwargs ):
        """
        Adds a field to this task.
        """
        if self.VERSION < 2:
            raise Exception( "Fields only exist in version 2 of the API" )
        
        if self.fields is None:
            self.fields = []
            
        field = {name: type}
        if kwargs:
            field.update( kwargs )
        self.fields.append( field )
        
    def dict( self ):
        dic = self.params.copy()
        if self.fields is not None:
            dic.update( {'fields': self.fields} )
        return dic
        
    
class Job(_API):
    
    def __init__( self, location = None, **job_params ):
        if location is not None and job_params:
            raise Exception( "You can't provide a location and job parameters at the same time" )
        if location is not None:
            self.location = location
            self._load()
        else:
            self.params = job_params
            self.tasks = []
            self.fields = None
        
    def _load( self ):
        self.params = Job._retrieve( self.location )
        if 'tasks' in self.params:
            self.tasks = self.params['tasks']
            del self.params['tasks']
        else:
            self.tasks = []
            
        if 'fields' in self.params:
            self.fields = self.params['fields']
            del self.params['fields']
        else:
            self.fields = None
        
    def _path( self ):
        """
        Returns the base path of jobs depending on the API version.
        """
        if self.VERSION == 1:
            return 'api/v1/job/'
        elif self.VERSION == 2:
            return 'api/v2/job/'
        raise Exception( 'Sorry, version %d is not supported by the library yet!' % self.VERSION )
        
    def get_param( self, name ):
        """
        Gets the specified parameter from this job.
        """
        return self.params[name]

    def set_params( self, **params ):
        """
        Sets parameters of this job.
        """
        self.params.update( params )
        
    def add_task( self, task ):
        """
        Adds a task to this job.
        """
        if task.__class__ == Task:
            self.tasks.append( task )
        else:
            raise ValueError( "`task` must be an instance of the Task class" )
    
    def add_field( self, name, type, **kwargs ):
        """
        Adds a field to this job.
        """
        if self.VERSION < 2:
            raise Exception( "Fields only exist in version 2 of the API" )
        
        if self.fields is None:
            self.fields = []
            
        field = {name: type}
        if kwargs:
            field.update( kwargs )
        self.fields.append( field )
    
    def dict( self ):
        dic = self.params.copy()
        if self.fields is not None:
            dic.update( {'fields': self.fields} )
        if self.tasks is not None:
            tasks = self.tasks
            if len( self.tasks ) and self.tasks[0].__class__ == Task:
                tasks = [t.dict() for t in tasks]
            dic.update( {'tasks': tasks} )
        return dic
    

class MobileWorks:
    """
    This class is used to login to MobileWorks and keeps track of the user credentials and
    the DOMAIN used for the API. 
    """
    
    credentials = None
    DOMAIN = 'https://work.mobileworks.com/'
    PROFILE_PATH = 'api/v1/userprofile/'
    
    @classmethod
    def login( cls, username, password ):
        cls.credentials = base64.encodestring( username + ':' + password )[:-1]
        try:
            headers, content = _API._make_request(cls.DOMAIN + cls.PROFILE_PATH)
            return json.loads( content )['objects'][0]
#            return _API._make_request(cls.DOMAIN + cls.PROFILE_PATH)['objects'][0]
        except Exception, e:
            print e
            cls.credentials = None
            raise Exception( "Login failed! To reset your password, please go to '%saccounts/password_reset/'" % cls.DOMAIN )
    
        
    @classmethod
    def local(cls, port = 8000):
        cls.DOMAIN = 'http://localhost:%d/' % port
    
    @classmethod    
    def staging(cls):
        cls.DOMAIN = 'https://staging.mobileworks.com/'
        
    @classmethod
    def sandbox(cls):
        cls.DOMAIN = 'https://sandbox.mobileworks.com/'
        
    @classmethod
    def production(cls):
        cls.DOMAIN = 'https://work.mobileworks.com/'
        
    @classmethod
    def version( cls, v = None ):
        if v == None:
            return _API.VERSION
        elif type( v ) == int:
            _API.VERSION = v
        else:
            raise Exception( 'Version must be an integer!' )
