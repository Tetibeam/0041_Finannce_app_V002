"""
Cython化スクリプト for batch/lib

batch/libディレクトリ内の全Pythonファイルをコンパイルして、
バイナリモジュール(.pyd/.so)を生成します。

使用方法:
    python cythonize_batch_lib.py              # 通常実行
    python cythonize_batch_lib.py --dry-run    # ドライラン(実際にはコンパイルしない)
    python cythonize_batch_lib.py --clean      # 中間ファイルをクリーンアップ
"""

import os
import sys
import shutil
import argparse
from pathlib import Path
from setuptools import setup, Extension
from Cython.Build import cythonize

# プロジェクトルートディレクトリ
PROJECT_ROOT = Path(__file__).parent.absolute()
BATCH_LIB_DIR = PROJECT_ROOT / "batch" / "lib"


def find_python_files(directory):
    """指定ディレクトリ内の全.pyファイルを検索"""
    py_files = []
    for file in directory.glob("*.py"):
        # __init__.pyは除外
        if file.name != "__init__.py":
            py_files.append(file)
    return sorted(py_files)


def create_extensions(py_files):
    """Cython Extension オブジェクトのリストを作成"""
    extensions = []
    for py_file in py_files:
        # モジュール名を生成 (例: batch.lib.agg_asset_cleaning)
        relative_path = py_file.relative_to(PROJECT_ROOT)
        module_name = str(relative_path.with_suffix("")).replace(os.sep, ".")
        
        extensions.append(
            Extension(
                module_name,
                [str(py_file)],
                # コンパイラ最適化オプション
                extra_compile_args=["/O2"] if sys.platform == "win32" else ["-O3"],
            )
        )
    return extensions


def cleanup_build_files():
    """ビルド中間ファイルをクリーンアップ"""
    print("\n🧹 クリーンアップ中...")
    
    # buildディレクトリを削除
    build_dir = PROJECT_ROOT / "build"
    if build_dir.exists():
        shutil.rmtree(build_dir)
        print(f"  ✓ 削除: {build_dir}")
    
    # .cファイルと.cppファイルを削除
    for ext in ["*.c", "*.cpp"]:
        for file in BATCH_LIB_DIR.glob(ext):
            file.unlink()
            print(f"  ✓ 削除: {file.name}")
    
    print("✅ クリーンアップ完了")


def main():
    parser = argparse.ArgumentParser(description="batch/libディレクトリをCython化")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="実際にはコンパイルせず、対象ファイルのみ表示"
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="ビルド中間ファイルをクリーンアップして終了"
    )
    parser.add_argument(
        "--keep-c",
        action="store_true",
        help="中間Cファイルを保持(デフォルトでは削除)"
    )
    
    args = parser.parse_args()
    
    # クリーンアップモード
    if args.clean:
        cleanup_build_files()
        return
    
    print("=" * 60)
    print("🔧 Cython化スクリプト for batch/lib")
    print("=" * 60)
    
    # Pythonファイルを検索
    py_files = find_python_files(BATCH_LIB_DIR)
    
    if not py_files:
        print("❌ エラー: batch/lib内にPythonファイルが見つかりません")
        sys.exit(1)
    
    print(f"\n📁 対象ディレクトリ: {BATCH_LIB_DIR}")
    print(f"📄 対象ファイル数: {len(py_files)}個\n")
    
    for i, py_file in enumerate(py_files, 1):
        print(f"  {i:2d}. {py_file.name}")
    
    # ドライランモード
    if args.dry_run:
        print("\n✅ ドライラン完了(実際のコンパイルは実行されませんでした)")
        return
    
    # Cythonのインストール確認
    try:
        import Cython
        print(f"\n✓ Cython バージョン: {Cython.__version__}")
    except ImportError:
        print("\n❌ エラー: Cythonがインストールされていません")
        print("   以下のコマンドでインストールしてください:")
        print("   pip install Cython")
        sys.exit(1)
    
    # Extensionオブジェクトを作成
    extensions = create_extensions(py_files)
    
    print("\n🔨 コンパイル開始...")
    print("-" * 60)
    
    # Cythonコンパイル実行
    try:
        setup(
            name="batch_lib_cython",
            ext_modules=cythonize(
                extensions,
                compiler_directives={
                    'language_level': "3",  # Python 3
                    'embedsignature': True,  # docstringを保持
                },
                build_dir="build",
            ),
            script_args=['build_ext', '--inplace'],
        )
        
        print("-" * 60)
        print("✅ コンパイル完了!")
        
        # コンパイル結果の確認
        compiled_files = list(BATCH_LIB_DIR.glob("*.pyd")) + list(BATCH_LIB_DIR.glob("*.so"))
        print(f"\n📦 生成されたバイナリファイル: {len(compiled_files)}個")
        for file in sorted(compiled_files):
            size_kb = file.stat().st_size / 1024
            print(f"  ✓ {file.name} ({size_kb:.1f} KB)")
        
        # 中間ファイルのクリーンアップ
        if not args.keep_c:
            print("\n🧹 中間ファイルをクリーンアップ中...")
            cleanup_build_files()
        
        print("\n" + "=" * 60)
        print("🎉 すべての処理が完了しました!")
        print("=" * 60)
        print("\n次のステップ:")
        print("  1. batch/lib内に.pyd/.soファイルが生成されていることを確認")
        print("  2. 既存のスクリプトを実行して動作確認")
        print("     例: python batch/init_db.py")
        print("\n注意:")
        print("  - .pyd/.soファイルは元の.pyファイルより優先的にインポートされます")
        print("  - デバッグが必要な場合は.pyd/.soファイルを削除してください")
        
    except Exception as e:
        print(f"\n❌ エラーが発生しました: {e}")
        print("\nトラブルシューティング:")
        print("  - Windows: Visual Studio Build Toolsがインストールされているか確認")
        print("  - Linux/Mac: gcc/clangがインストールされているか確認")
        sys.exit(1)


if __name__ == "__main__":
    main()
