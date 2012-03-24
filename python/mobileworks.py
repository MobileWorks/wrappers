import urllib2, json, base64


class Request( urllib2.Request ):
    
    def __init__( self, url, data = None, headers = {},
                 origin_req_host = None, unverifiable = False, method = None ):
        self._method = method
        urllib2.Request.__init__( self, url, data, headers, origin_req_host, unverifiable )
    
    def get_method( self ):
        return self._method if self._method else urllib2.Request.get_method( self )
    

class MobileWorks:
    
    PRODUCTION = False
    
    def __init__( self, username, password ):
        self.credentials = base64.encodestring( username + ':' + password )[:-1]
        if self.PRODUCTION:
            self.task_url = 'https://work.mobileworks.com/api/v2/task/'
            self.job_url = 'https://work.mobileworks.com/api/v2/job/'
        else:
            self.task_url = 'https://staging.mobileworks.com/api/v2/task/'
            self.job_url = 'https://staging.mobileworks.com/api/v2/job/'
        

    def request( self, url, method = None, postData = None ):
        req = Request( url, method = method, data = postData )
        req.add_header( 'Authorization', 'Basic ' + self.credentials )
        response = urllib2.urlopen( req )
        content = response.read()
        response.close()
        return json.loads( content )
    
    def postTask( self, **taskParams ):
        """
        Posts a task to MobileWorks and returns the url of the created task.
        """
        return self.request( self.task_url, 'POST', json.dumps( taskParams ) )['Location']
        
    def retrieveTask( self, taskUrl ):
        """
        Gets the result of the task located in `taskUrl`.
        """
        return self.request( taskUrl )
    
    def deleteTask( self, taskUrl ):
        """
        Deletes a task.
        """
        return self.request( taskUrl, 'DELETE' )
        
    def postJob( self, **jobParams ):
        """
        Posts a job to MobileWorks and returns the url of the created job.
        """
        return self.request( self.job_url, 'POST', json.dumps( jobParams ) )['Location']
    
    def retrieveJob( self, jobUrl ):
        """
        Gets the result of the job located in `jobUrl`.
        """
        return self.request( jobUrl )
    
    def deleteJob( self, jobUrl ):
        """
        Deletes a job.
        """
        return self.request( jobUrl, 'DELETE' )

def main():
    print 'hello!'

if __name__ == '__main__':
    main()
    w = MobileWorks( 'prayag', 'root' )
