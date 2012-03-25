import urllib2, json, base64


class Request( urllib2.Request ):
    """
    This class is used to allow urllib2 to send DELETE requests.
    """
    
    def __init__( self, url, data = None, headers = {},
                 origin_req_host = None, unverifiable = False, method = None ):
        self._method = method
        urllib2.Request.__init__( self, url, data, headers, origin_req_host, unverifiable )
    
    def get_method( self ):
        return self._method if self._method else urllib2.Request.get_method( self )
    

class API:
    
    task_url = 'https://work.mobileworks.com/api/v2/task/'
    job_url = 'https://work.mobileworks.com/api/v2/job/'
    
    def __init__( self, username, password ):
        self.credentials = base64.encodestring( username + ':' + password )[:-1]

    def makeRequest( self, url, method = None, postData = None ):
        """
        Creates and sends an HTTP request.
        """
        req = Request( url, method = method, data = postData )
        req.add_header( 'Authorization', 'Basic ' + self.credentials )
        
        try:
            response = urllib2.urlopen( req )
            content = response.read()
            response.close()
            return json.loads( content )
        except urllib2.HTTPError, e:
            if e.code >= 500:
                raise Exception( 'HTTP %d: A server error occured' % e.code )
            else:
                raise Exception( 'HTTP %d: %s' % ( e.code, e.read() ) )
    
    def postTask( self, **taskParams ):
        """
        Posts a task to API and returns the URL of the created task.
        """
        return self.makeRequest( self.task_url, 'POST', json.dumps( taskParams ) )['Location']
        
    def retrieveTask( self, taskUrl ):
        """
        Gets the information of the task located in `taskUrl`.
        """
        return self.makeRequest( taskUrl )
    
    def deleteTask( self, taskUrl ):
        """
        Deletes the task located in `taskUrl`.
        """
        return self.makeRequest( taskUrl, 'DELETE' )
        
    def postJob( self, **jobParams ):
        """
        Posts a job to API and returns the URL of the created job.
        """
        return self.makeRequest( self.job_url, 'POST', json.dumps( jobParams ) )['Location']
    
    def retrieveJob( self, jobUrl ):
        """
        Gets the information of the job located in `jobUrl`.
        """
        return self.makeRequest( jobUrl )
    
    def deleteJob( self, jobUrl ):
        """
        Deletes the job located in `jobUrl`.
        """
        return self.makeRequest( jobUrl, 'DELETE' )


def example():
    mw = API( 'username', 'password' )
    taskLocation = mw.postTask( instructions = 'instructions', resource = '', field = [{'Name':'t'}] )
    task = mw.retrieveTask( taskLocation )
    print task
