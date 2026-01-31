"""
微信公众号登录自动化脚本
使用 Playwright 控制浏览器进行扫码登录
"""

import asyncio
import os
from pathlib import Path

from playwright.async_api import TimeoutError as PlaywrightTimeoutError
from playwright.async_api import async_playwright

# 配置变量
WX_LOGIN = "https://mp.weixin.qq.com/"
WX_HOME = "https://mp.weixin.qq.com/cgi-bin/home"
STATIC_DIR = Path(__file__).parent.parent / "data" / "static"
QRCODE_PATH = STATIC_DIR / "wx_qrcode.png"

# 二维码最小有效大小（字节），小于此值说明获取失败
QRCODE_MIN_SIZE = 364


def print_info(message: str):
    """输出信息日志"""
    print(f"[INFO] {message}")


def print_success(message: str):
    """输出成功日志"""
    print(f"[SUCCESS] {message}")


def print_warning(message: str):
    """输出警告日志"""
    print(f"[WARNING] {message}")


def print_error(message: str):
    """输出错误日志"""
    print(f"[ERROR] {message}")


async def cleanup_resources(page=None, context=None, browser=None, driver=None):
    """清理所有资源

    Args:
        page: 页面对象
        context: 上下文对象
        browser: 浏览器对象
        driver: Playwright driver对象
    """
    cleanup_errors = []

    # 按顺序清理资源
    if page:
        try:
            await page.close()
        except Exception as e:
            cleanup_errors.append(f"页面关闭失败: {str(e)}")

    if context:
        try:
            await context.close()
        except Exception as e:
            cleanup_errors.append(f"上下文关闭失败: {str(e)}")

    if browser:
        try:
            await browser.close()
        except Exception as e:
            cleanup_errors.append(f"浏览器关闭失败: {str(e)}")

    if driver:
        try:
            await driver.stop()
        except Exception as e:
            cleanup_errors.append(f"Driver停止失败: {str(e)}")

    if cleanup_errors:
        print_warning(f"资源清理时发生错误: {'; '.join(cleanup_errors)}")
    else:
        print_info("资源清理完成")


async def validate_qrcode():
    """验证二维码是否有效

    Returns:
        bool: 二维码是否有效
    """
    try:
        if not QRCODE_PATH.exists():
            print_error(f"二维码文件不存在: {QRCODE_PATH}")
            return False

        file_size = QRCODE_PATH.stat().st_size
        if file_size < QRCODE_MIN_SIZE:
            print_error(
                f"二维码文件大小异常: {file_size} 字节（最小要求: {QRCODE_MIN_SIZE} 字节）"
            )
            return False

        print_info(f"二维码验证通过，文件大小: {file_size} 字节")
        return True

    except OSError as e:
        print_error(f"验证二维码文件时出错: {str(e)}")
        return False


async def main():
    """执行登录流程"""
    # 创建 static 目录
    try:
        STATIC_DIR.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        print_error(f"创建静态文件目录失败: {str(e)}")
        return

    # 初始化变量
    driver = None
    browser = None
    context = None
    page = None

    try:
        # 启动 Playwright driver
        print_info("正在启动 Playwright driver...")
        driver = await async_playwright().start()

        # 启动浏览器
        print_info("正在启动浏览器...")
        browser = await driver.chromium.launch(headless=False)

        # 创建上下文
        print_info("正在创建浏览器上下文...")
        context = await browser.new_context(
            viewport={"width": 1280, "height": 720}, locale="zh-CN"
        )

        # 创建页面
        page = await context.new_page()

        # 1. 打开登录页面
        print_info(f"正在打开登录页面: {WX_LOGIN}")
        try:
            await page.goto(WX_LOGIN, timeout=30000, wait_until="domcontentloaded")
            print_success("登录页面加载成功")
        except PlaywrightTimeoutError:
            raise Exception("打开登录页面超时，请检查网络连接")
        except Exception as e:
            raise Exception(f"打开登录页面失败: {str(e)}")

        # 等待页面加载完成
        print_info("等待页面完全加载...")
        try:
            await page.wait_for_load_state("networkidle", timeout=10000)
        except PlaywrightTimeoutError:
            print_warning("页面加载未完全达到 networkidle 状态，继续执行")

        # 2. 获取并保存二维码
        print_info("正在等待二维码加载...")
        try:
            await page.wait_for_selector("img[src*='qrcode']", timeout=15000)
        except PlaywrightTimeoutError:
            raise Exception("二维码元素加载超时，请检查页面结构是否变化")

        try:
            qrcode = await page.query_selector("img[src*='qrcode']")
            if not qrcode:
                raise Exception("无法找到二维码元素")

            await qrcode.screenshot(path=str(QRCODE_PATH))
            print_info(f"二维码已保存至: {QRCODE_PATH}")
        except Exception as e:
            raise Exception(f"二维码截图失败: {str(e)}")

        # 验证二维码有效性
        if not await validate_qrcode():
            raise Exception("二维码验证失败，请重新运行程序")

        # 3. 等待扫码登录
        print_info("等待扫码登录（最长等待时间: 60秒）...")
        try:
            # 监听导航事件，提供更好的用户体验
            async def handle_navigation(frame):
                current_url = frame.url
                if WX_HOME in current_url:
                    print_success(f"检测到跳转: {current_url}")

            page.on("framenavigated", handle_navigation)
            await page.wait_for_url(WX_HOME, timeout=60000)
            print_success("登录成功！")

        except PlaywrightTimeoutError:
            print_warning("扫码登录超时（60秒），请重新运行程序进行扫码登录")
            raise
        except Exception as e:
            print_error(f"等待登录过程中发生错误: {str(e)}")
            raise

    except KeyboardInterrupt:
        print_warning("\n用户中断执行")
        raise

    except PlaywrightTimeoutError as e:
        print_error(f"操作超时: {str(e)}")

    except OSError as e:
        print_error(f"系统错误: {str(e)}")

    except Exception as e:
        print_error(f"执行失败: {str(e)}")

    finally:
        # 4. 清理所有资源
        print_info("正在清理浏览器资源...")
        await cleanup_resources(
            page=page, context=context, browser=browser, driver=driver
        )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print_warning("\n程序被用户中断")
    except Exception as e:
        print_error(f"程序异常退出: {str(e)}")
