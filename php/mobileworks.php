<?php


class MobileWorks {

	private $credentials = '';
	private $task_url = 'https://work.mobileworks.com/api/v2/task/';
	private $job_url = 'https://work.mobileworks.com/api/v2/job/';

	function __construct( $username, $password ) {
		if ( !extension_loaded( 'curl' ) ) {
			throw new Exception( 'CURL is not installed!' );
		}
		$this->credentials = "$username:$password";
	}

	/**
	 * Creates and sends a request to the specified $url using the specified $method.
	 * @param string $url The URL of the request.
	 * @param string $method The method of the request (GET/POST/DELETE).
	 * @param null|string|array $postData  The data to be posted (optional).
	 * @return array The array representation of the returned JSON object.
	 * @throws Exception
	 */
	function makeRequest( $url, $method = 'GET', $postData = null ) {
		$req = curl_init( $url );
		curl_setopt( $req, CURLOPT_CUSTOMREQUEST, $method );
		if ( $method == 'POST' && !is_null( $postData ) ) {
			curl_setopt( $req, CURLOPT_POSTFIELDS, $postData );
		}
		curl_setopt( $req, CURLOPT_RETURNTRANSFER, true );
		curl_setopt( $req, CURLOPT_HTTPAUTH, CURLAUTH_BASIC );
		curl_setopt( $req, CURLOPT_USERPWD, $this->credentials );

		$result = curl_exec( $req );
		if ( curl_errno( $req ) ) {
			curl_close( $req );
			throw new Exception( curl_error( $req ) );
		}
		$httpCode = curl_getinfo( $req, CURLINFO_HTTP_CODE );
		echo $httpCode, PHP_EOL;
		curl_close( $req );
		if ( $httpCode >= 500 ) {
			throw new Exception( "HTTP $httpCode: A server error occured" );
		}
		if ( $httpCode >= 300 ) {
			throw new Exception( "HTTP $httpCode: $result" );
		}
		return get_object_vars( json_decode( $result ) );
	}

	/**
	 * Posts a task to MobileWorks and returns the URL of the created task.
	 * @param array $taskParams The parameters of the task to be created.
	 * @return string The URL of the created task.
	 */
	function postTask( $taskParams ) {
		$response = $this->makeRequest( $this->task_url, 'POST', json_encode( $taskParams ) );
		return $response['Location'];
	}

	/**
	 * Gets the information of the task located in $taskUrl.
	 * @param string $taskUrl The URL of the task to be retrieved.
	 * @return array The task's information.
	 */
	function retrieveTask( $taskUrl ) {
		return $this->makeRequest( $taskUrl );
	}

	/**
	 * Deletes the task located in $taskUrl.
	 * @param string $taskUrl The URL of the task to be deleted.
	 * @return array
	 */
	function deleteTask( $taskUrl ) {
		return $this->makeRequest( $taskUrl, 'DELETE' );
	}

	/**
	 * Posts a job to MobileWorks and returns the URL of the created job.
	 * @param array $jobParams The parameters of the job to be created.
	 * @return string The URL of the created job.
	 */
	function postJob( $jobParams ) {
		$response = $this->makeRequest( $this->job_url, 'POST', json_encode( $jobParams ) );
		return $response['Location'];
	}

	/**
	 * Gets the information of the job located in $jobUrl.
	 * @param string $jobUrl The URL of the job to be retrieved.
	 * @return array The job's information.
	 */
	function retrieveJob( $jobUrl ) {
		return $this->makeRequest( $jobUrl );
	}

	/**
	 * Deletes the job located in $jobUrl.
	 * @param string $jobUrl The URL of the job to be deleted.
	 * @return array
	 */
	function deleteJob( $jobUrl ) {
		return $this->makeRequest( $jobUrl, 'DELETE' );
	}

}
