class AccountFields:
    @staticmethod
    def fields(ds):
        return (
            ds.Account.id,
            ds.Account.active,
            ds.Account.addressCity,
            ds.Account.addressZip,
            ds.Account.availableCredits,
            ds.Account.country,
            ds.Account.createdAt,
            ds.Account.customHeaderColor,
            ds.Account.customLogo,
            ds.Account.customMenuColor,
            ds.Account.limitLevelsMax,
            ds.Account.limitPagesMax,
            ds.Account.maxCrawlRate,
            ds.Account.name,
            ds.Account.packagePlan,
            ds.Account.phone,
            ds.Account.rawID,
            ds.Account.serpentCrawlerEnabled,
            ds.Account.timezone,
            ds.Account.updatedAt,
            ds.Account.apiCallbackUrl,
            ds.Account.accountManagers,
        )

    @staticmethod
    def settings_fields(ds):
        return (
            ds.AccountSetting.code,
            ds.AccountSetting.dataType,
            ds.AccountSetting.description,
            ds.AccountSetting.limit,
            ds.AccountSetting.name,
            ds.AccountSetting.source,
            ds.AccountSetting.type,
            ds.AccountSetting.unit,
            ds.AccountSetting.visible,
        )

    @staticmethod
    def locations_fields(ds):
        return (
            ds.Location.code,
            ds.Location.enabled,
            ds.Location.id,
            ds.Location.name,
            ds.Location.rawID,
            ds.Location.type,
        )

    @staticmethod
    def subscription_fields(ds):
        return (
            ds.AccountSubscription.analyzeAvailable,
            ds.AccountSubscription.automateAvailable,
            ds.AccountSubscription.automatorAvailable,
            ds.AccountSubscription.billingAt,
            ds.AccountSubscription.googleDataStudioAvailable,
            ds.AccountSubscription.impactAvailable,
            ds.AccountSubscription.jsRenderingAvailable,
            ds.AccountSubscription.monitorAvailable,
            ds.AccountSubscription.segmentationAvailable,
            ds.AccountSubscription.status,
            ds.AccountSubscription.currentBillingPeriod.select(ds.DateTimeRange.start, ds.DateTimeRange.end),
            ds.AccountSubscription.plan.select(
                ds.AccountSubscriptionPlan.code,
                ds.AccountSubscriptionPlan.minCommitmentPeriod,
                ds.AccountSubscriptionPlan.name,
                ds.AccountSubscriptionPlan.period,
                ds.AccountSubscriptionPlan.status,
            ),
        )

    @staticmethod
    def subscription_addons_fields(ds):
        return (
            ds.AccountSubscriptionAddon.code,
            ds.AccountSubscriptionAddon.integrationType,
            ds.AccountSubscriptionAddon.name,
            ds.AccountSubscriptionAddon.type,
            ds.AccountSubscriptionAddon.status,
        )
