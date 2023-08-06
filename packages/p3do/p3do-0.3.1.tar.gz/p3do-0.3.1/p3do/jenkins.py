#!/usr/bin/env python3

from jenkinsapi.jenkins import Jenkins

def _get_server_instance(api_user: str, api_key: str):
    jenkins_url = "https://ci2.semantic-web.at/"
    server = Jenkins(jenkins_url, username=api_user, password=api_key, timeout=30)
    return server

def run_build(job: str, branch: str, api_user: str, api_key: str):
    print(f"Running job {job} on branch {branch}")


    print(f"Getting server instance")
    server = _get_server_instance(api_user, api_key)
    print(f"Got server instance {server}")
    params = {'branch': branch}

    # This will start the job and will return a QueueItem object which
    # can be used to get build results
    jk_job = server[job]
    print(f"Got job: {jk_job}")
    qi = jk_job.invoke(build_params=params)
    print(f"Got job invocation: {qi}")

    print(f"Blocking until building")
    qi.block_until_building()
    print(f"Started build")
    print(f"{qi.get_build()}")
    print(f"{qi.get_build().get_build_url()}")
