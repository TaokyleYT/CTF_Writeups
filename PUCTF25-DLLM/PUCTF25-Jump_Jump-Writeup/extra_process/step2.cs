using System;
using UnityEngine;
using UnityEngine.UI;

// Token: 0x02000002 RID: 2
public class player2 : MonoBehaviour
{
    // Token: 0x06000001 RID: 1 RVA: 0x00002050 File Offset: 0x00000250
    private void Start()
    {
        string text = this.dude2.GetComponent<global::UnityEngine.UI.Text>().text;
        byte[] array = Convert.FromBase64String(text)
        Texture2D texture2D = new Texture2D(1, 1);
        texture2D.LoadImage(img);
        Rect rect = new Rect(0f, 0f, (float)texture2D.width, (float)texture2D.height);
        Vector2 vector = new Vector2(0f, 0f);
        this.dude.GetComponent<SpriteRenderer>().sprite = Sprite.Create(texture2D, rect, vector);
    }

    // Token: 0x04000003 RID: 3
    [SerializeField]
    private GameObject dude;

    // Token: 0x04000004 RID: 4
    [SerializeField]
    private GameObject dude2;
}
