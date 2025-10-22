using System;
using UnityEngine;
using UnityEngine.UI;

// Token: 0x02000002 RID: 2
public class player2 : MonoBehaviour
{
    // Token: 0x06000001 RID: 1 RVA: 0x00002050 File Offset: 0x00000250
    private void Start()
    {
        this.string1 = this.init_string1();
        if (1 > 0)
        {
            this.func1();
        }
    }

    // Token: 0x06000003 RID: 3 RVA: 0x00002074 File Offset: 0x00000274
    private string init_string1()
    {
        int num = (int)((byte)(97 | 0));
        char c = (char)(((num >> 2 << 2) | (num & 3)) ^ 0);
        string text = this.cast_to_char((int)c).ToString() ?? "";
        string text2 = this.init_text2();
        string text3 = ("." + text2) ?? "";
        string text4 = ((text3 != null) ? (text + text3)) : "");
        string text5 = ((text4.Length > 0) ? (text4 ?? "") : text4);
        return text5;
    }

    // Token: 0x06000007 RID: 7 RVA: 0x0000211B File Offset: 0x0000031B
    private char cast_to_char(int c)
    {
        return (char)(c | (c & 0));
    }


    // Token: 0x06000009 RID: 9 RVA: 0x0000212C File Offset: 0x0000032C
    private string init_text2()
    {
        return string.Concat(new string[]
        {
            "d",
            "a",
            "t",
            "",
            "",
            "",
            "",
            ""
        });
    }

    // Token: 0x06000010 RID: 16 RVA: 0x000021BF File Offset: 0x000003BF
    private void func1()
    {
        this.sprite1 = this.init_sprite1(this.string1);
        this.set_sprite(this.sprite1, this.dude);
    }

    // Token: 0x06000011 RID: 17 RVA: 0x000021E5 File Offset: 0x000003E5
    private void set_sprite(Sprite sprite, GameObject gameobject)
    {
        gameobject.GetComponent<SpriteRenderer>().sprite = sprite;
    }

    // Token: 0x06000012 RID: 18 RVA: 0x000021F4 File Offset: 0x000003F4
    private Sprite init_sprite1(string String)
    {
        string text = this.dude2.GetComponent<global::UnityEngine.UI.Text>().text;
        byte[] array = this.init_array(text);
        Texture2D texture2D = ((array != null) ? this.check_array(array) : new Texture2D(0, 0));
        Rect rect = ((texture2D.width > 0) ? this.init_rect(texture2D) : default(Rect));
        Vector2 vector = new Vector2(0f, 0f);
        if (!(texture2D != null) || rect.width < 0f)
        {
            return null;
        }
        return this.init_sprite(texture2D, rect, vector);
    }

    // Token: 0x06000015 RID: 21 RVA: 0x00002290 File Offset: 0x00000490
    private byte[] init_array(string text)
    {
        byte[] array = ((text != "") ? Convert.FromBase64String(text) : new byte[0]);
        if (array.Length == 0)
        {
            return new byte[1];
        }
        return array;
    }

    // Token: 0x06000016 RID: 22 RVA: 0x000022C8 File Offset: 0x000004C8
    private Texture2D check_array(byte[] array)
    {
        Texture2D texture2D = new Texture2D(1, 1);
        if (texture2D != null && array != null)
        {
            texture2D.LoadImage(array);
        }
        return texture2D ?? new Texture2D(1, 1);
    }

    // Token: 0x06000017 RID: 23 RVA: 0x00002300 File Offset: 0x00000500
    private Rect init_rect(Texture2D texture2d)
    {
        if (!(texture2d != null))
        {
            return default(Rect);
        }
        return new Rect(0f, 0f, (float)texture2d.width, (float)texture2d.height);
    }

    // Token: 0x0600001A RID: 26 RVA: 0x00002351 File Offset: 0x00000551
    private Sprite init_sprite(Texture2D texture2d, Rect rect, Vector2 vector)
    {
        if (!(texture2d != null))
        {
            return null;
        }
        return Sprite.Create(texture2d, rect, vector);
    }

    // Token: 0x04000001 RID: 1
    private string string1;

    // Token: 0x04000002 RID: 2
    private Sprite sprite1;

    // Token: 0x04000003 RID: 3
    [SerializeField]
    private GameObject dude;

    // Token: 0x04000004 RID: 4
    [SerializeField]
    private GameObject dude2;
}