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
	 * @param null|string|array $post_data  The data to be posted (optional).
	 * @return array The array representation of the returned JSON object.
	 * @throws Exception
	 */
	private function make_request( $url, $method = 'GET', $post_data = null ) {
		$req = curl_init( $url );
		curl_setopt( $req, CURLOPT_CUSTOMREQUEST, $method );
		if ( $method == 'POST' && !is_null( $post_data ) ) {
			curl_setopt( $req, CURLOPT_POSTFIELDS, $post_data );
		}
		curl_setopt( $req, CURLOPT_RETURNTRANSFER, true );
		curl_setopt( $req, CURLOPT_HTTPAUTH, CURLAUTH_BASIC );
		curl_setopt( $req, CURLOPT_USERPWD, $this->credentials );

		$result = curl_exec( $req );
		if ( curl_errno( $req ) ) {
			curl_close( $req );
			throw new Exception( curl_error( $req ) );
		}
		$http_code = curl_getinfo( $req, CURLINFO_HTTP_CODE );
		echo $http_code, PHP_EOL;
		curl_close( $req );
		if ( $http_code >= 500 ) {
			throw new Exception( "HTTP $http_code: A server error occured" );
		}
		if ( $http_code >= 300 ) {
			throw new Exception( "HTTP $http_code: $result" );
		}
		return get_object_vars( json_decode( $result ) );
	}

	/**
	 * Posts a task to MobileWorks and returns the URL of the created task.
	 * @param array $task_params The parameters of the task to be created.
	 * @return string The URL of the created task.
	 */
	function postTask( $task_params ) {
		$response = $this->make_request( $this->task_url, 'POST', json_encode( $task_params ) );
		return $response['Location'];
	}

	/**
	 * Gets the information of the task located in $taskUrl.
	 * @param string $task_url The URL of the task to be retrieved.
	 * @return array The task's information.
	 */
	function retrieveTask( $task_url ) {
		return $this->make_request( $task_url );
	}

	/**
	 * Deletes the task located in $taskUrl.
	 * @param string $task_url The URL of the task to be deleted.
	 * @return array
	 */
	function deleteTask( $task_url ) {
		return $this->make_request( $task_url, 'DELETE' );
	}

	/**
	 * Posts a job to MobileWorks and returns the URL of the created job.
	 * @param array $job_params The parameters of the job to be created.
	 * @return string The URL of the created job.
	 */
	function postJob( $job_params ) {
		$response = $this->make_request( $this->job_url, 'POST', json_encode( $job_params ) );
		return $response['Location'];
	}

	/**
	 * Gets the information of the job located in $jobUrl.
	 * @param string $job_url The URL of the job to be retrieved.
	 * @return array The job's information.
	 */
	function retrieveJob( $job_url ) {
		return $this->make_request( $job_url );
	}

	/**
	 * Deletes the job located in $jobUrl.
	 * @param string $job_url The URL of the job to be deleted.
	 * @return array
	 */
	function deleteJob( $job_url ) {
		return $this->make_request( $job_url, 'DELETE' );
	}

}
