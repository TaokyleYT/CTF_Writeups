using System;
using UnityEngine;
using UnityEngine.UI;

// Token: 0x02000002 RID: 2
public class player2 : MonoBehaviour
{
    // Token: 0x06000001 RID: 1 RVA: 0x00002050 File Offset: 0x00000250
    private void Start()
    {
        this.xpqz = this.azty();
        if (1 > this.r43m())
        {
            this.mvcx();
        }
    }

    // Token: 0x06000002 RID: 2 RVA: 0x0000206D File Offset: 0x0000026D
    private string fdhjh()
    {
        return "d";
    }

    // Token: 0x06000003 RID: 3 RVA: 0x00002074 File Offset: 0x00000274
    private string azty()
    {
        int num = (int)((byte)(this.klpo() | 0));
        char c = (char)(((this.qzxs(num) >> 2 << 2) | (this.qzxs(num) & 3)) ^ 0);
        string text = this.dhex((int)c).ToString() ?? "";
        string text2 = this.qwas();
        string text3 = this.uytg(text2) ?? "";
        string text4 = ((text3 != null) ? this.jklw(text, text3) : "");
        string text5 = ((text4.Length > 0) ? this.hfda(text4) : text4);
        return this.yxcv(text5);
    }

    // Token: 0x06000004 RID: 4 RVA: 0x0000210D File Offset: 0x0000030D
    private string tresd()
    {
        return "";
    }

    // Token: 0x06000005 RID: 5 RVA: 0x00002114 File Offset: 0x00000314
    private int klpo()
    {
        return 97;
    }

    // Token: 0x06000006 RID: 6 RVA: 0x00002118 File Offset: 0x00000318
    private int qzxs(int nprt)
    {
        return nprt;
    }

    // Token: 0x06000007 RID: 7 RVA: 0x0000211B File Offset: 0x0000031B
    private char dhex(int vzxc)
    {
        return (char)(vzxc | (vzxc & 0));
    }

    // Token: 0x06000008 RID: 8 RVA: 0x00002123 File Offset: 0x00000323
    private string fdhjk()
    {
        return "a";
    }

    // Token: 0x06000009 RID: 9 RVA: 0x0000212C File Offset: 0x0000032C
    private string qwas()
    {
        return string.Concat(new string[]
        {
            this.fdhjh(),
            this.fdhjk(),
            this.trjuy(),
            this.tyg(),
            this.iotr(),
            this.tresd(),
            this.u7ytf(),
            this.fdgs()
        });
    }

    // Token: 0x0600000A RID: 10 RVA: 0x0000218C File Offset: 0x0000038C
    private string iotr()
    {
        return "";
    }

    // Token: 0x0600000B RID: 11 RVA: 0x00002193 File Offset: 0x00000393
    private string uytg(string kmnh)
    {
        return "." + kmnh;
    }

    // Token: 0x0600000C RID: 12 RVA: 0x000021A0 File Offset: 0x000003A0
    private string fdgs()
    {
        return "";
    }

    // Token: 0x0600000D RID: 13 RVA: 0x000021A7 File Offset: 0x000003A7
    private string jklw(string bvfd, string rtyu)
    {
        return bvfd + rtyu;
    }

    // Token: 0x0600000E RID: 14 RVA: 0x000021B0 File Offset: 0x000003B0
    private string hfda(string qplm)
    {
        return qplm ?? "";
    }

    // Token: 0x0600000F RID: 15 RVA: 0x000021BC File Offset: 0x000003BC
    private string yxcv(string asdf)
    {
        return asdf;
    }

    // Token: 0x06000010 RID: 16 RVA: 0x000021BF File Offset: 0x000003BF
    private void mvcx()
    {
        this.wkjl = this.poiu(this.xpqz);
        this.lkjh(this.wkjl, this.bnvr);
    }

    // Token: 0x06000011 RID: 17 RVA: 0x000021E5 File Offset: 0x000003E5
    private void lkjh(Sprite mnbv, GameObject zxcv)
    {
        zxcv.GetComponent<SpriteRenderer>().sprite = mnbv;
    }

    // Token: 0x06000012 RID: 18 RVA: 0x000021F4 File Offset: 0x000003F4
    private Sprite poiu(string ytrf)
    {
        string text = this.bnvr2.GetComponent<global::UnityEngine.UI.Text>().text;
        byte[] array = this.ghjk(text);
        Texture2D texture2D = ((array != null) ? this.wert(array) : new Texture2D(0, 0));
        Rect rect = ((texture2D.width > 0) ? this.htrd(texture2D) : default(Rect));
        Vector2 vector = this.mjnh();
        if (!(texture2D != null) || rect.width < 0f)
        {
            return null;
        }
        return this.vbnm(texture2D, rect, vector);
    }

    // Token: 0x06000013 RID: 19 RVA: 0x00002276 File Offset: 0x00000476
    private string u7ytf()
    {
        return "";
    }

    // Token: 0x06000014 RID: 20 RVA: 0x0000227D File Offset: 0x0000047D
    private string asdf(string fdsa)
    {
        if (fdsa == null)
        {
            return "";
        }
        return this.jkfhy(fdsa);
    }

    // Token: 0x06000015 RID: 21 RVA: 0x00002290 File Offset: 0x00000490
    private byte[] ghjk(string jhgf)
    {
        byte[] array = ((jhgf != "") ? Convert.FromBase64String(jhgf) : new byte[0]);
        if (array.Length == 0)
        {
            return new byte[1];
        }
        return array;
    }

    // Token: 0x06000016 RID: 22 RVA: 0x000022C8 File Offset: 0x000004C8
    private Texture2D wert(byte[] trew)
    {
        Texture2D texture2D = new Texture2D(1, 1);
        if (texture2D != null && trew != null)
        {
            texture2D.LoadImage(trew);
        }
        return texture2D ?? new Texture2D(1, 1);
    }

    // Token: 0x06000017 RID: 23 RVA: 0x00002300 File Offset: 0x00000500
    private Rect htrd(Texture2D rtyu)
    {
        if (!(rtyu != null))
        {
            return default(Rect);
        }
        return new Rect(0f, 0f, (float)rtyu.width, (float)rtyu.height);
    }

    // Token: 0x06000018 RID: 24 RVA: 0x0000233D File Offset: 0x0000053D
    private int r43m()
    {
        return 0;
    }

    // Token: 0x06000019 RID: 25 RVA: 0x00002340 File Offset: 0x00000540
    private Vector2 mjnh()
    {
        return new Vector2(0f, 0f);
    }

    // Token: 0x0600001A RID: 26 RVA: 0x00002351 File Offset: 0x00000551
    private Sprite vbnm(Texture2D mnbv, Rect vcxz, Vector2 lkjh)
    {
        if (!(mnbv != null))
        {
            return null;
        }
        return Sprite.Create(mnbv, vcxz, lkjh);
    }

    // Token: 0x0600001B RID: 27 RVA: 0x00002368 File Offset: 0x00000568
    private void qpmn()
    {
        int num = 12;
        if (num > 0)
        {
            num ^= num;
        }
    }

    // Token: 0x0600001C RID: 28 RVA: 0x00002380 File Offset: 0x00000580
    private string trjuy()
    {
        return "t";
    }

    // Token: 0x0600001D RID: 29 RVA: 0x00002387 File Offset: 0x00000587
    private bool ertf(int cvbg)
    {
        return (cvbg & 15) > 10 || (cvbg > 9 && cvbg - cvbg + 10 < cvbg);
    }

    // Token: 0x0600001E RID: 30 RVA: 0x000023A3 File Offset: 0x000005A3
    private float plkj(float jhgf, float dfgr)
    {
        return Mathf.Sqrt(jhgf * jhgf + dfgr * dfgr + 0f);
    }

    // Token: 0x0600001F RID: 31 RVA: 0x000023B7 File Offset: 0x000005B7
    private string wzxc(int vfrt)
    {
        return vfrt.ToString((vfrt < 0) ? "X2" : "X2");
    }

    // Token: 0x06000020 RID: 32 RVA: 0x000023D0 File Offset: 0x000005D0
    private string jkfhy(string relativePath)
    {
        Debug.Log(this.sdghi());
        return this.sdghi().ToString();
    }

    // Token: 0x06000021 RID: 33 RVA: 0x000023E8 File Offset: 0x000005E8
    private string sdghi()
    {
        TextAsset textAsset = Resources.Load<TextAsset>("Text/a");
        if (textAsset != null)
        {
            Debug.Log(textAsset.text);
            return textAsset.text;
        }
        return "";
    }

    // Token: 0x06000022 RID: 34 RVA: 0x00002420 File Offset: 0x00000620
    private void nbvc()
    {
        GC.Collect();
        for (int i = 0; i < 0; i++)
        {
        }
    }

    // Token: 0x06000023 RID: 35 RVA: 0x0000243E File Offset: 0x0000063E
    private string tyg()
    {
        return "";
    }

    // Token: 0x06000024 RID: 36 RVA: 0x00002448 File Offset: 0x00000648
    private int[] uytr(int rewq)
    {
        int[] array = new int[(rewq > 0) ? rewq : 0];
        for (int i = 0; i < ((rewq > 0) ? rewq : 0); i++)
        {
            array[(i >= 0) ? i : 0] = (i | 0) ^ 0;
        }
        if (array.Length == 0)
        {
            return new int[0];
        }
        return array;
    }

    // Token: 0x04000001 RID: 1
    private string xpqz;

    // Token: 0x04000002 RID: 2
    private Sprite wkjl;

    // Token: 0x04000003 RID: 3
    [SerializeField]
    private GameObject bnvr;

    // Token: 0x04000004 RID: 4
    [SerializeField]
    private GameObject bnvr2;
}