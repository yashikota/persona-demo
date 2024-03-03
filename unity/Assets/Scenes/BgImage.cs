using System.Collections;
using UnityEngine;
using System.Runtime.InteropServices;
using System;
using Microsoft.Win32.SafeHandles;

public class BgImage : MonoBehaviour
{
    Texture2D texture;
    string MemoryName = "bgImage";
    static int w = 640;
    static int h = 360;
    static UInt32 size = (UInt32)(w * h * 4);

    [DllImport("kernel32.dll", SetLastError = true, CharSet = CharSet.Auto)]
    static extern SafeFileHandle OpenFileMapping(
        uint dwDesiredAccess,
        bool bInheritHandle,
        string lpName);

    [DllImport("kernel32.dll", SetLastError = true)]
    static extern IntPtr MapViewOfFile(
        SafeFileHandle hFileMappingObject,
        UInt32 dwDesiredAccess,
        UInt32 dwFileOffsetHigh,
        UInt32 dwFileOffsetLow,
        UIntPtr dwNumberOfBytesToMap);

    const UInt32 STANDARD_RIGHTS_REQUIRED = 0x000F0000;
    const UInt32 SECTION_QUERY = 0x0001;
    const UInt32 SECTION_MAP_WRITE = 0x0002;
    const UInt32 SECTION_MAP_READ = 0x0004;
    const UInt32 SECTION_MAP_EXECUTE = 0x0008;
    const UInt32 SECTION_EXTEND_SIZE = 0x0010;
    const UInt32 SECTION_ALL_ACCESS = (STANDARD_RIGHTS_REQUIRED | SECTION_QUERY |
                                       SECTION_MAP_WRITE |
                                       SECTION_MAP_READ |
                                       SECTION_MAP_EXECUTE |
                                       SECTION_EXTEND_SIZE);
    const UInt32 FILE_MAP_ALL_ACCESS = SECTION_ALL_ACCESS;
    private SafeFileHandle handle;
    private IntPtr buffer;
    private Renderer _renderer;

    // Start is called before the first frame update
    void Start()
    {
        _renderer = GetComponent<Renderer>();
        texture = new Texture2D(w, h, TextureFormat.RGBA32, false);
        handle = OpenFileMapping(FILE_MAP_ALL_ACCESS, false, MemoryName);
        buffer = MapViewOfFile(handle, FILE_MAP_ALL_ACCESS, 0, 0, new UIntPtr(size));
    }
    // Update is called once per frame
    void Update()
    {
        texture.LoadRawTextureData(buffer, (int)size);
        texture.Apply();
        _renderer.material.mainTexture= texture;
    }
}