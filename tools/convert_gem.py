#!/usr/bin/env python3
"""
convert_gem.py: PC-98 .GEM ファイルを PNG 画像に変換するスクリプト

使い方:
    python3 convert_gem.py <input_dir> <output_dir>

<input_dir> 内の .GEM ファイルをすべて PNG に変換し、<output_dir> に出力します。
"""
import os
import sys
from PIL import Image

def convert_gem_file(src_path: str, dst_dir: str) -> None:
    """
    .GEM ファイルのバイナリを読み込んで PNG に変換し保存する
    ファイル構造:
      ・オフセット 0-1: 画像幅 (リトルエンディアン 2 バイト)
      ・オフセット 2-3: 画像高さ (リトルエンディアン 2 バイト)
      ・オフセット 4- (4+256*3-1): パレット情報 (RGB 各 1 バイト × 256 エントリ)
      ・残り: 画素インデックス配列 (幅×高さ バイト)
    """
    # ファイル読み込み
    data = open(src_path, 'rb').read()
    if len(data) < 4 + 256*3:
        raise ValueError(f"Invalid GEM file: {src_path}")

    # ヘッダー解析
    width = int.from_bytes(data[0:2], 'little')
    height = int.from_bytes(data[2:4], 'little')
    palette_data = data[4:4 + 256*3]
    pixel_data = data[4 + 256*3:]

    # ピクセル数確認
    expected = width * height
    if len(pixel_data) < expected:
        raise ValueError(f"Unexpected pixel data size in {src_path}: {len(pixel_data)} vs {expected}")

    # 画像生成
    img = Image.frombytes('P', (width, height), pixel_data[:expected])
    img.putpalette(palette_data)
    img = img.convert('RGBA')

    # 保存
    base = os.path.splitext(os.path.basename(src_path))[0]
    dst_path = os.path.join(dst_dir, f"{base}.png")
    img.save(dst_path)
    print(f"Converted: {src_path} -> {dst_path}")


def main():
    if len(sys.argv) != 3:
        print("Usage: python3 convert_gem.py <input_dir> <output_dir>")
        sys.exit(1)

    src_dir = sys.argv[1]
    dst_dir = sys.argv[2]
    os.makedirs(dst_dir, exist_ok=True)

    for fname in os.listdir(src_dir):
        if fname.lower().endswith('.gem'):
            convert_gem_file(os.path.join(src_dir, fname), dst_dir)

if __name__ == '__main__':
    main()
