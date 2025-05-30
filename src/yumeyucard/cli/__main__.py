from datetime import datetime
from pathlib import Path
import sys
import click
import toml
from github import Github
from github import Auth

from ..__init__ import __version__



@click.group()
@click.version_option(version=__version__, message="YumeyuCard version: %(version)s")
@click.pass_context
def cli(ctx: click.Context) -> None:
    """YumeyuCard!"""
    pass


@cli.command()
@click.option('--token','-t', envvar='GITHUB_ACCESS_TOKEN', help="登录凭据：通行令牌", required=False)
def login(token: str) -> None:
    """登录 Github"""

    if not token:
        token = click.prompt("请输入 GitHub 访问令牌", type=str, hide_input=False, show_default=False)

    auth = Auth.Token(token)
    g = Github(auth=auth)

    for i, repo in enumerate(g.get_user().get_repos()):
        click.echo(f"Repo {i + 1}: {repo.name}")



@cli.command()
@click.option("--root","-r" , envvar="YMYC_ROOT", help="YumeyuCard 根目录")
@click.pass_context
def init(ctx: click.Context, root : str | Path) -> None:
    """手动初始化 YumeyuCard 根目录"""
    
    if not root:
        root  = Path.home() / ".ymyc"
        click.echo(f"未指定根目录，使用默认目录: {root}")

    # 检查 root 目录是否存在 且为空目录
    click.echo(f"正在初始化 YumeyuCard 根目录: {root}")
    if not Path(root).is_dir():
        click.echo(f"根目录 '{root}' 不存在.")
        if click.confirm(f"是否创建目录 '{root}'?", abort=False):
            Path(root).mkdir(parents=True, exist_ok=True)

    dotYmyc: Path = Path(root) / '.ymyc'
    if any(Path(root).iterdir()):
        if not dotYmyc.exists():
            click.echo(f"错误: 请指定一个空目录")
            root = click.prompt(f"输入根目录地址", type=str, default="~/.ymyc", show_default=True, show_choices=True)

        if dotYmyc.exists():
            meta = toml.load(dotYmyc)
            last_update = meta.get('last_update', None)
            if last_update:
                last_update = datetime.fromisoformat(last_update)
                click.echo(f"上次使用: {last_update.strftime('%Y-%m-%d %H:%M:%S')}")
            meta['last_update'] = datetime.now().isoformat()
            toml.dump(meta, dotYmyc.open('w', encoding='utf-8'))
    else:
        click.echo(f"初始化目录中...")
        # STEP 1: 创建 .ymyc 元数据标记文件
        click.echo(f"创建 .ymyc 元数据标记文件")
        meta = {
            'last_update': datetime.now().isoformat(),
            'version': __version__,
            'root': str(Path(root).resolve())
        }
        dotYmyc.touch(exist_ok=True)
        click.echo(f"创建 .ymyc 元数据标记文件成功: {dotYmyc}")
        with dotYmyc.open('w', encoding='utf-8') as f:
            toml.dump(meta, f)

        # STEP 2: 创建基本目录结构
        click.echo(f"创建基本目录结构")
        (Path(root) / 'cards').mkdir(parents=True, exist_ok=True)
        (Path(root) / 'io').mkdir(parents=True, exist_ok=True)

    click.echo(f"YumeyuCard 根目录初始化完成: {root}")



    ctx.ensure_object(dict)
    ctx.obj["root"] = root


if __name__ == "__main__":
    cli()