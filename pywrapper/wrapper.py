import urllib, urllib2, json, base64


class Task:
    
    params = ['instructions', 'fields', 'resource', 'taskid', 'resourcetype', 'priority', 'workflow', 'redundancy']
    
    instructions = ''
    fields = []
    
    def __init__( self, **kwargs ):
        for p in self.params:
            if p in kwargs:
                setattr( self, p, kwargs[p] )
            
    def addField( self, name, type ):
        self.fields.append( {name: type} )
        
    def toJson( self ):
        d = {}
        for p in self.params:
            if hasattr( self, p ):
                d[p] = getattr( self, p )
        return json.dumps( d )
        

class Wrapper:
    
    PRODUCTION = False
    
    def __init__( self, username, password ):
        self.credentials = base64.encodestring( username + ':' + password )[:-1]
        if self.PRODUCTION:
            self.task_url = "https://work.mobileworks.com/api/v2/task/"
        else:
            self.task_url = "https://staging.mobileworks.com/api/v2/task/"
        

    def request( self, taskID = None ):
        url = self.task_url
        if taskID is not None:
            url += '%s/' % taskID
        req = urllib2.Request( url )
        req.add_header( 'Authorization', 'Basic ' + self.credentials )
        return req
    
    def getTaskID( self, taskLocation ):
        """
        Parses the task ID from the task location ( url )
        """
        token = '/task/'
        pos = taskLocation.rfind( token ) + len( token )
        return taskLocation[pos:].strip( '/' )

    def postTask( self, task ):
        """
        Posts a task to MobileWorks.
        `task` must be an instance of the Task class.
        """
        response = urllib2.urlopen( self.request(), task.toJson() )
        return self.getTaskID( json.loads( response.read() )['Location'] )
        
    def taskResult( self, taskID ):
        """
        Gets the result for the task specified by `taskID`
        """
        return json.loads( urllib2.urlopen( self.request( taskID ) ).read() )


def main():
    print 'hello!'

if __name__ == '__main__':
    main()
    w = Wrapper( 'prayag', 'root' )
