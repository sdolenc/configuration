Usage
#####

Start the container with this:

``docker run -ti -e GO_SERVER=your.go.server.ip_or_host edx/go-agent-marketing``

If you need to start a few GoCD agents together, you can of course use the
shell to do that. Start a few agents in the background, like this:

``for each in 1 2 3; do docker run -d --link angry_feynman:go-server edx/go-agent-marketing; done``

Getting into the container
##########################

Sometimes, you need a shell inside the container (to create test repositories,
etc). docker provides an easy way to do that:

``docker exec -i -t CONTAINER-ID /bin/bash``

To check the agent logs, you can do this:

``docker exec -i -t CONTAINER-ID tail -f /var/log/go-agent/go-agent.log``

Agent Configuration
###################

The go-agent expects it's configuration to be found at
``/var/lib/go-agent/config/``. Sharing the configuration between containers is
done by mounting a volume at this location that contains any configuration
files necessary.

**Example docker run command:**
``docker run -ti -v /tmp/go-agent/conf:/var/lib/go-agent/config -e GO_SERVER=gocd.sandbox.edx.org 718d75c467c0 bash``

`How to setup auto registration for remote agents`_

Building and Uploading the container to ECS
###########################################

-  Build and tag the go-agent docker image

   -  Follow the README in the go-agent directory to build and tag for go-agent-marketing.

-  Copy the Acquia GitHub private key to this path:

   -  ``docker/build/go-agent-marketing/files/acquia_github_key.pem``
   -  A dummy key is in the repo file.
   -  The actual private key is kept in LastPass - see DevOps for access.
   -  WARNING: Do *NOT* commit/push the real private key to the public
      configuration repo!

-  Copy the Agent Auto Register Key to this path:

   -  ``docker/build/go-agent-marketing/config/autoregister.properties``
   -  A dummy key is in the repo file.
   -  NOTE: this key *must* match the agentAutoRegisterKey in the server configuration
   -  WARNING: Do *NOT* commit/push the real private key to the public
      configuration repo!

-  Create image

   -  This must be run from the root of the configuration repository
   -  ``docker build -f docker/build/go-agent-marketing/Dockerfile .``
   -  or
   -  ``make docker.test.go-agent-marketing``

-  Log docker in to AWS

   -  Assume the role of the account you wish to log in to

      -  ``source assume_role.sh <account name>``

   -  ``sh -c `aws ecr get-login --region us-east-1```

      -  You might need to remove the ``-e`` option returned by that command in
         order to successfully login.

-  Tag image

   -  ``docker tag <image_id> ############.dkr.ecr.us-east-1.amazonaws.com/prod-tools-goagent-marketing:latest``
   -  ``docker tag <image_id> ############.dkr.ecr.us-east-1.amazonaws.com/prod-tools-goagent-marketing:<version_number>``

-  upload:

   -  ``docker push ############.dkr.ecr.us-east-1.amazonaws.com/edx/release-pipeline/prod-tools-goagent-marketing:latest``
   -  ``docker push ############.dkr.ecr.us-east-1.amazonaws.com/edx/release-pipeline/prod-tools-goagent-marketing:<version_number>``

.. _How to setup auto registration for remote agents: https://docs.go.cd/current/advanced_usage/agent_auto_register.html
