# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import botocore
import ssl

PROTOCOLS = {
    "1.3": getattr(ssl, "PROTOCOL_TLSv1_3", None),
    "1.2": getattr(ssl, "PROTOCOL_TLSv1_2", None),
}


def context_from_config(ciphers, ssl_version):
    def _get_ssl_context(self):
        return botocore.httpsession.create_urllib3_context(
            ssl_version=ssl_version, ciphers=ciphers
        )

    return _get_ssl_context


def patch_botocore(session=None):
    session = session if session else botocore.session.Session()
    config = session.get_scoped_config()

    # Get the user provided tls_ciphers, and add a +HIGH to set HIGH
    # as the floor for each user-provided option.
    # If nothing is provided by the user, then HIGH is the floor.
    tls_ciphers = filter(None, config.get("tls_ciphers", "").split(":"))
    high_selection = [f"{cipher}+HIGH" for cipher in tls_ciphers]
    user_selection = ":".join(high_selection) if high_selection else "HIGH"

    # Explicitly exclude bad values. This should remove known bad ciphers, even
    # if they are explicitly added
    ciphers = ":".join(
        [
            user_selection,
            "!MEDIUM",
            "!LOW",
            "!aNULL",
            "!eNULL",
            "!ADH",
            "!MD5",
            "!RC4",
            "!RC2",
            "!SHA1",
            "!DES",
            "!3DES",
            "!EXP",
        ]
    )
    print(ciphers)
    ssl_version = PROTOCOLS.get(config.get("tls_version"), None)
    botocore.httpsession.URLLib3Session._get_ssl_context = context_from_config(
        ciphers, ssl_version
    )


def set_ciphers(parsed_args, **kwargs):
    profile = parsed_args.profile
    session = (
        botocore.session.Session(profile=profile) if profile else kwargs["session"]
    )
    patch_botocore(session)


def awscli_initialize(cli):
    cli.register("top-level-args-parsed", set_ciphers)
