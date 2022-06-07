## aws-iot-remote-asset-heatlh-monitoring

This repository was created to support the AWS IoT blog post Empowering operations: A scalable Remote asset health monitoring solution (link), and host the following files:

* ### bootstrap.sh 
Executes the bootstrap installation for the AWS Cloud9 instance which the user will use to work with the blog post content.
* ### start.sh
Check dependencies and start the simulator.py script.
* ### simulator.py
An AwSIoTPython sdk example file containing a simple PubSub communication model with AWS IoT core, and a simulated dataset. 
* ### create_thing.py
Uses AWS CLI commands to create resources in AWS IoT core, things, policies and certificates.
* ### create_iotrules.py
Uses AWS CLI commands to create resources in AWS IoT core, IoT rules,
* ### create_iotsitewise_assets.py
Uses AWS CLI commands to create resources in AWS IoT SiteWise, assets.
* ### create_grafana_dashboards.py
Uses AWS CLI commands to create resources in an Amazon managed grafana workspace.
* ### datagen 
Directory with JSON objects used for the simulated dataset 
* ### iot_rules
Directory containing an template JSON object used by the create_iotrules.py file


The following files:
## Security

[![security: bandit](https://img.shields.io/badge/security-bandit-yellow.svg)](https://github.com/PyCQA/bandit)

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This library is licensed under the MIT-0 License. See the LICENSE file.

