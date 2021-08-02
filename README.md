Here
-------

一个 [MCDReforged](https://github.com/Fallen-Breath/MCDReforged) 的插件

输入`!!here help`查阅本插件的帮助信息

当玩家输入 `!!here` 时, 玩家的坐标将被显示并且将被发光效果高亮（如果配置启用的话）

当玩家输入 `!!where <player>` 时, 会显示`<player>`的坐标并高亮（如果配置启用的话）, 如果在后面加上`-a`则会广播给所有人, 加上`-s`则只有自己会看到（互斥）, 不添加额外参数的默认行为由配置文件规定

当管理员(具有配置文件中规定的权限等级以上的玩家或控制台)输入`!!here reload`时会重载该插件

当 MCDR 启动 rcon 时此插件可使用 rcon 来获得玩家信息，响应更快

配置文件默认值适用于一般生存服务器，如需修改请查阅[此处](./config.md)
（此处一般生存服务器指所有玩家均没有传送等OP功能权限的生存模式服务器)

![example](https://raw.githubusercontent.com/TISUnion/Here/MCDR/img.png)


