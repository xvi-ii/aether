import aenum
import attrs

from aether import const
from aether.core import utils
from aether.api import resources

class PremiumType(aenum.IntEnum):
    NONE            = 0
    NITRO_CLASSIC   = aenum.auto()
    NITRO           = aenum.auto()
    NITRO_BASIC     = aenum.auto()

class Flags(aenum.IntFlag):
    # undocumented flags from: https://flags.lewisakura.moe
    STAFF                           = 1 << 0
    PARTNER                         = aenum.auto()
    HYPESQUAD                       = aenum.auto()
    BUG_HUNTER_LEVEL_1              = aenum.auto()
    MFA_SMS                         = aenum.auto() # undocumented
    HYPESQUAD_ONLINE_HOUSE_1        = aenum.auto()
    HYPESQUAD_ONLINE_HOUSE_2        = aenum.auto()
    HYPESQUAD_ONLINE_HOUSE_3        = aenum.auto()
    PREMIUM_EARLY_SUPPORTER         = aenum.auto()
    TEAM_PSEUDO_USER                = aenum.auto()
    INTERNAL_APPLICATION            = aenum.auto() # undocumented
    SYSTEM                          = aenum.auto() # undocumented
    HAS_UNREAD_URGENT_MESSAGES      = aenum.auto() # undocumented
    BUG_HUNTER_LEVEL_2              = aenum.auto()
    UNDERAGE_DELETED                = aenum.auto() # undocumented
    VERIFIED_BOT                    = aenum.auto()
    VERIFIED_DEVELOPER              = aenum.auto()
    CERTIFIED_MODERATOR             = aenum.auto()
    BOT_HTTP_INTERACTIONS           = aenum.auto()
    SPAMMER                         = aenum.auto() # undocumented
    DISABLE_PREMIUM                 = aenum.auto() # undocumented
    ACTIVE_DEVELOPER                = aenum.auto()
    HIGH_GLOBAL_RATE_LIMIT          = aenum.auto() # undocumented
    DELETED                         = aenum.auto() # undocumented
    DISABLED_SUSPICIOUS_ACTIVITY    = aenum.auto() # undocumented
    SELF_DELETED                    = aenum.auto() # undocumented
    PREMIUM_DISCRIMINATOR           = aenum.auto() # undocumented
    USED_DESKTOP_CLIENT             = aenum.auto() # undocumented
    USED_MOBILE_CLIENT              = aenum.auto() # undocumented
    DISABLED                        = aenum.auto() # undocumented
    VERIFIED_EMAIL                  = aenum.auto() # undocumented
    QUARANTINED                     = aenum.auto() # undocumented
    COLLABORATOR                    = aenum.auto() # undocumented
    RESTRICTED_COLLABORATOR         = aenum.auto() # undocumented

@attrs.define(kw_only=True)
class User(resources.Object):
    id: resources.Snowflake[str]
    username: str
    discriminator: str
    global_name: str | None
    avatar: resources.Asset | None
    bot: const.Maybe[bool] = const.empty
    system: const.Maybe[bool] = const.empty
    mfa_enabled: const.Maybe[bool] = const.empty
    banner: const.Maybe[resources.Asset] | None = const.empty
    accent_color: const.Maybe[int] | None = const.empty
    locale: const.Maybe[str] = const.empty
    verified: const.Maybe[bool] = const.empty
    email: const.Maybe[str] | None = const.empty
    flags: const.Maybe[int] = const.empty
    premium_type: const.Maybe[PremiumType] = const.empty
    public_flags: const.Maybe[Flags] = const.empty
    avatar_decoration: const.Maybe[resources.Asset] | None = const.empty
    
    def __attrs_post_init__(self):
        self.avatar = resources.Asset.resolve(
            resources.Endpoint.CDN.USER_AVATAR,
            user_id=self.id,
            user_avatar=self.avatar
        )
        if utils.contains(self.banner):
            self.banner = resources.Asset.resolve(
                resources.Endpoint.CDN.USER_BANNER,
                user_id=self.id,
                user_banner=self.banner
            )
        if utils.contains(self.avatar_decoration):
            self.avatar_decoration = resources.Asset.resolve(
                resources.Endpoint.CDN.USER_AVATAR_DECORATION,
                user_id=self.id,
                user_avatar_decoration=self.avatar_decoration
            )