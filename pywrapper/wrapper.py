import urllib2, json, base64


class Request( urllib2.Request ):
    
    def __init__( self, url, data = None, headers = {},
                 origin_req_host = None, unverifiable = False, method = None ):
        self._method = method
        urllib2.Request.__init__( self, url, data, headers, origin_req_host, unverifiable )
    
    def get_method( self ):
        return self._method if self._method else urllib2.Request.get_method( self )
    

class Wrapper:
    
    PRODUCTION = False
    
    def __init__( self, username, password ):
        self.credentials = base64.encodestring( username + ':' + password )[:-1]
        if self.PRODUCTION:
            self.task_url = 'https://work.mobileworks.com/api/v2/task/'
            self.job_url = 'https://work.mobileworks.com/api/v2/job/'
        else:
            self.task_url = 'https://staging.mobileworks.com/api/v2/task/'
            self.job_url = 'https://staging.mobileworks.com/api/v2/job/'
        

    def request( self, url, method = None ):
        req = Request( url, method = method )
        req.add_header( 'Authorization', 'Basic ' + self.credentials )
        return req
    
    def parseTaskID( self, taskUrl ):
        """
        Parses the task ID from the task location ( url )
        """
        token = '/task/'
        pos = taskUrl.rfind( token ) + len( token )
        return taskUrl[pos:].rstrip( '/' )

    def postTask( self, **taskParams ):
        """
        Posts a task to MobileWorks and returns the url of the created task.
        """
        response = urllib2.urlopen( self.request( self.task_url ), json.dumps( taskParams ) )
        content = response.read()
        response.close()
        return json.loads( content )['Location']
        
    def retrieveTask( self, taskUrl ):
        """
        Gets the result for the task located in `taskUrl`.
        """
        return json.loads( urllib2.urlopen( self.request( taskUrl ) ).read() )
    
    def deleteTask( self, taskUrl ):
        """
        Deletes a task.
        """
        try:
            response = urllib2.urlopen( self.request( taskUrl, 'DELETE' ) )
            return response
        except urllib2.HTTPError, e:
            return e
        
    def postJob( self, **jobParams ):
        """
        Posts a job to MobileWorks and returns the url of the created job.
        """
        response = urllib2.urlopen( self.request( self.job_url ), json.dumps( jobParams ) )
        content = response.read()
        response.close()
        return json.loads( content )['Location']
    
    def retrieveJob( self, jobUrl ):
        """
        Gets the result for the job located in `jobUrl`.
        """
        return json.loads( urllib2.urlopen( self.request( jobUrl ) ).read() )
    
    def deleteJob( self, jobUrl ):
        """
        Deletes a job.
        """
        try:
            response = urllib2.urlopen( self.request( jobUrl, 'DELETE' ) )
            return response
        except urllib2.HTTPError, e:
            return e

def main():
    print 'hello!'

if __name__ == '__main__':
    main()
    w = Wrapper( 'prayag', 'root' )
