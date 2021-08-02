 # 插件配置指南
 
 ## 基本配置
 
插件配置文件路径由代码中标记为可编辑内容的`CONFIG_FILE`规定

配置文件具有如下基本配置:

1. `command_prefix`: 自定义指令前缀, `here`键指定的是广播自己坐标的指令前缀(默认`"!!here"`), `where`则是查询他人坐标(默认`"!!where"`)

2. `permission_requirement`: 最小权限等级, 设置大于4的值可以完全禁用该功能, `here`键指定的是广播自己坐标的最小权限等级（默认0）, `where`键则是查询他人坐标的最小权限等级(默认2), `admin`则控制本插件的一些管理功能的权限(默认3)
 
3. `highlight_time`: 玩家被高亮时间, `here`键控制广播自己坐标的发光时间(默认15）, `where`则是查询他人坐标(默认为0）

4. `display_waypoint`: 是否显示一段可用于为客户端小地图mod添加坐标点的可点击文本(默认均为`true`), `voxelmap`键适用于Voxelmap, `xaeros_minimap`适用于Xaero's Minimap 

5. `console_here_text`: 在服务端使用广播自己坐标的指令时的广播信息, 设置为非字符串(如`true`, `false`或`[]`等)则会禁用服务端使用该指令(默认值: `"这有个鬼才运维试图广播服务端的坐标"`)

6. `query_timeout`: 当插件使用非rcon手段时的最大响应时间, 超时则判定玩家不存在(默认3)

7. `where_default_broadcast`: 查询他人坐标不添加额外参数时的默认行为(默认值为`false`, 即仅显示给命令源)

8. `click_to_teleport`: 显示文本中的坐标信息是否可以点击传送, 需要玩家具有op权限, 一般生存服务器可放心使用(默认值为`true`)

9. `location_protect`: 玩家位置保护相关设定:

    'enable_whitelist'和`enable_blacklist`分别启用查询白名单和黑名单, 权限等级不满足本配置文件中权限要求`admin`级别要求的玩家查询他人坐标时, 白名单启用后仅有`whitelist`中的玩家可被查询, 黑名单启用后`blacklist`中的玩家不可被查询, `protected_text`为不具备`admin`权限的玩家查询受保护的玩家坐标时返回的信息。
    
    默认值: `enable_whitelist`: False, `enable_blacklist`: True, `whitelist`和`blacklist`均为`[]`(即空列表), `protected_text`: "§c他在你心里!§r"(即红色的"他在你心里!")

## 高级配置

这部分配置一般仅适用于调试排障

### 位于配置文件中的隐藏选项:

该隐藏部分不被包含在默认配置文件中, 需要管理员自行添加, 故无默认值

`disable_rcon`: 设置为`true`时强制不使用rcon获取玩家信息, 建议仅当服务端rcon连接正常但是查询不到玩家时将其启用, 适用于当前MCDR的rcon连接别的服务端时
