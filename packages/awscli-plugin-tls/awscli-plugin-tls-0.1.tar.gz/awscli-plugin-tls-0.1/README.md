# awscli-plugin-tls

> A plugin for configuring TLS parameters advertised by `awscli`

This awscli plugin allows users to configure TLS versions and
cipher suites used when connecting to AWS services via the CLI.
It can additionally be used by boto3 applications to enable
those configurations through their `~/.aws/config`.

Most users will not need this plugin, as the `urllib3` utilizes secure defaults
for these settings.

## Disclaimer

You are responsible for properly configuring this plugin to ensure secure
cipher suites are used when negotiating the TLS connection.
Using this plugin, it is possible for clients to configure less-secure cipher
suites than what is provided by default. Please only use this plugin if you
have a requirement to enforce specific cipher suites or TLS versions in your
applications, and are familiar with how to utilize OpenSSL's cipherlist to select
cipher suites. Be sure to test and ensure you are not advertising insecure
cipher suites before using in a production setting.

## Installation

```
pip install .
```

## Configuration

Edit your `~/.aws/config` to include the following plugin definition:

If you are using the v1 AWS CLI, you can just add the plugin:

```
[plugins]
tls = awscli_plugin_tls
```

If you are using the v2 AWS CLI, you need to also specify the `cli_legacy_plugin_path`, which should
specify where your `pip` packages are installed.

```
[plugins]
cli_legacy_plugin_path = <path to your python3.7/site-packages>
tls = awscli_plugin_tls
```

Additionally, under any profile (either a named profile or `[default]`, configure
the appropriate settings:

```
[default]
tls_ciphers = ECDHE+AES256+AESGCM
tls_version = 1.2
...other settings
```

## Usage

### AWS CLI

Once configured, you can use your AWS CLI as normal:

```
aws s3 ls
```

### Boto3

You can also patch boto3 applications by calling the `patch_botocore` method directly:

```
import boto3
from awscli_plugin_tls import patch_botocore
patch_botocore()

s3 = boto3.client('s3')
print(s3.list_buckets())
```

If your boto3 application needs to use a named profile, you can pass in your own
session object using that profile name:

```
import boto3
from awscli_plugin_tls import patch_botocore
session = botocore.session.Session(profile="your-named-profile")
patch_botocore(session)

s3 = boto3.client('s3')
print(s3.list_buckets())
botocore.session.Session(profile=profile)
```

## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This project is licensed under the Apache-2.0 License.
