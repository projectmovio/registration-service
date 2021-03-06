from aws_cdk import core

import aws_cdk.aws_cognito as cognito
from aws_cdk.aws_certificatemanager import Certificate


class Login(core.Stack):

    def __init__(self, app: core.App, id: str, domain_name: str, cert_arn, **kwargs) -> None:
        super().__init__(app, id, **kwargs)
        self.cert_arn = cert_arn
        self.domain_name = domain_name
        self._create_userpool()

    def _create_userpool(self):
        user_pool = cognito.UserPool(
            self,
            "movio",
            account_recovery=cognito.AccountRecovery.EMAIL_ONLY,
            auto_verify=cognito.AutoVerifiedAttrs(email=True, phone=False),
            mfa=cognito.Mfa.OFF,
            mfa_second_factor=cognito.MfaSecondFactor(otp=True, sms=False),
            self_sign_up_enabled=False,
            sign_in_aliases=cognito.SignInAliases(email=True, username=True),
            standard_attributes=cognito.StandardAttributes(
                email=cognito.StandardAttribute(mutable=False, required=True),
            ),
            user_invitation=cognito.UserInvitationConfig(
                email_subject="Moshan email verification",
                email_body="Thanks for signing up to moshan! Your username is {username} and temporary password is {####}\nYou can now login at https://moshan.tv",
            ),
            user_verification=cognito.UserVerificationConfig(
                email_subject="Moshan email verification",
                email_body="Thanks for signing up to moshan! Verify your account by clicking on {##Verify Email##}",
                email_style=cognito.VerificationEmailStyle.LINK
            ),
        )

        user_pool.add_client(
            "moshan",
            auth_flows=cognito.AuthFlow(refresh_token=True),
            o_auth=cognito.OAuthSettings(
                flows=cognito.OAuthFlows(authorization_code_grant=True),
                callback_urls=["https://moshan.tv/callback.html", "https://beta.moshan.tv/callback.html"],
                scopes=[cognito.OAuthScope.EMAIL, cognito.OAuthScope.OPENID, cognito.OAuthScope.PROFILE]),
            prevent_user_existence_errors=True,
        )

        cert = Certificate.from_certificate_arn(self, "domainCert", self.cert_arn)
        user_pool.add_domain(
            "CognitoDomain",
            custom_domain=cognito.CustomDomainOptions(
                domain_name=self.domain_name,
                certificate=cert
            )
        )
