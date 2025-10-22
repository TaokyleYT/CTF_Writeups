using System;
using System.Collections.Generic;
using UnityEngine;

// Token: 0x02000004 RID: 4
public class playerscript : MonoBehaviour
{
	// Token: 0x06000028 RID: 40 RVA: 0x000024C0 File Offset: 0x000006C0
	private void Start()
	{
		this.rb = base.GetComponent<Rigidbody2D>();
		this.mainCamera = Camera.main;
		if (this.mainCamera == null)
		{
			Debug.LogError("Main camera not found!");
		}
		this.lastPlatformPosition = base.transform.position + new Vector3(0f, -50f, 0f);
		this.messages = new List<string>
		{
			"You're doing great!", "Well done!", "You're doing great!", "Why are you still jumping?", "Stop jumping!", "You're wasting your time!", "Why are you still jumping?",
			"Stop jumping!", "You're wasting your time!", "Why are you still jumping?", "Stop jumping!", "You're wasting your time!", "Why are you still jumping?", "Stop jumping!", "You're wasting your time!", "Why are you still jumping?", "Stop jumping!",
			"Hint: The flag is at the end", "Hint: The flag is at the end", "Hint: The flag is at the end", "Hint: restart the game", "Hint: restart the game", "Hint: restart the game", "Hint: 1 + 1 = 2", "Hint: 1 + 1 = 2", "Hint: 1 + 1 = 2", "Hint: don't jump",
			"Hint: don't jump", "Hint: don't jump", "Hint: spacebar is broken", "Hint: spacebar is broken", "Hint: spacebar is broken", "You're wasting your time!", "Keep going!", "Great job!", "You're doing awesome!", "Keep it up!",
			"Fantastic!", "Amazing!", "You're unstoppable!", "Incredible!", "Outstanding!", "Superb!", "Excellent!", "Marvelous!", "Terrific!", "Spectacular!",
			"Remarkable!", "Brilliant!", "Phenomenal!", "Extraordinary!", "Exceptional!", "Wonderful!", "You're a star!", "Keep pushing!", "You're on fire!", "Unbelievable!",
			"You're a champion!", "You're a hero!", "You're a legend!", "You're a winner!", "You're amazing!", "You're fantastic!", "You're incredible!", "You're outstanding!", "You're superb!", "You're excellent!",
			"You're marvelous!", "You're terrific!", "You're spectacular!", "You're remarkable!", "You're brilliant!", "You're phenomenal!", "You're extraordinary!", "You're exceptional!", "You're wonderful!", "Keep climbing!",
			"You're doing great!", "You're a superstar!", "You're a rockstar!", "You're a warrior!", "You're a fighter!", "You're a conqueror!", "You're a master!", "You're a pro!", "You're a genius!", "You're a wizard!",
			"You're a magician!", "You're a guru!", "You're a sage!", "You're a virtuoso!", "You're a prodigy!", "You're a maestro!", "You're a genius!", "You're a whiz!", "You're a dynamo!", "You're a powerhouse!",
			"You're a juggernaut!", "You're a titan!", "You're a colossus!", "You're a giant!", "You're a behemoth!", "You're a leviathan!", "You're a mammoth!", "You're a monster!", "You're a beast!", "You're a legend!",
			"You're a myth!", "You're a god!", "You're a deity!", "You're a divinity!", "You're a celestial!", "You're a star!", "You're a sun!", "You're a moon!", "You're a planet!", "You're a galaxy!",
			"You're a universe!", "You're a cosmos!", "You're a nebula!", "You're a supernova!", "You're a black hole!", "You're a quasar!", "You're a pulsar!", "You're a comet", "You're a meteor!", "You're a meteorite!",
			"You're a meteoroid!", "You're a star!", "You're a sun!", "You're a moon!", "You are the universe!", "You are the cosmos!", "You are the galaxy!", "You are the nebula!", "You are the supernova!", "You are the black hole!",
			"You are the quasar!", "You are the pulsar!", "You are the comet!", "You are the meteor!", "You are the meteorite!", "You are the meteoroid!", "You are the star!", "You are the sun!", "You are the moon!", "You are the planet!",
			"You are the galaxy!", "You are the universe!", "You are the cosmos!", "You almost got the flag!", "You're almost there!", "You're so close!", "You're right there!", "You're on the edge!", "You're on the brink!", "You're on the verge!",
			"You're on the cusp!", "You're on the threshold!", "You're on the border!", "You're on the frontier!", "You're on the horizon!"
		};
		if (this.messageText == null)
		{
			Debug.LogError("Message Text component not assigned!");
		}
		for (int i = 1; i <= 6; i++)
		{
			this.GeneratePlatform();
		}
		if (this.messageText == null)
		{
			Debug.LogError("Message Text component not assigned!");
		}
	}

	// Token: 0x06000029 RID: 41 RVA: 0x00003D64 File Offset: 0x00001F64
	private void Update()
	{
		if (this.rb.velocity.y == 0f)
		{
			this.isJumping = false;
		}
		if (Input.GetKeyDown(KeyCode.Space) && !this.isJumping)
		{
			this.Jump();
			this.GeneratePlatform();
			this.showFloatingText(this.messages[Random.Range(0, Random.Range(0, this.messages.Count))], 300);
			this.jumpForce = 492f;
		}
		if (this.mainCamera != null)
		{
			float speed = 5f;

			// this.mainCamera.transform.position = new Vector3(base.transform.position.x, base.transform.position.y, this.mainCamera.transform.position.z);

            if (Input.GetKey(KeyCode.LeftArrow))
            {
                this.mainCamera.transform.Rotate(Vector3.up, -1f);
            }
            if (Input.GetKey(KeyCode.RightArrow))
            {
                this.mainCamera.transform.Rotate(Vector3.up, 1f);
            }
            if (Input.GetKey(KeyCode.UpArrow))
            {
                this.mainCamera.transform.Rotate(Vector3.right, 1f);
            }
            if (Input.GetKey(KeyCode.DownArrow))
            {
                this.mainCamera.transform.Rotate(Vector3.right, -1f);
            }
			

			if (Input.GetKey(KeyCode.W))
			{
				this.mainCamera.transform.Translate(Vector3.forward * speed * Time.deltaTime);
			}
			if (Input.GetKey(KeyCode.S))
			{
				this.mainCamera.transform.Translate(Vector3.back * speed * Time.deltaTime);
			}
			if (Input.GetKey(KeyCode.A))
			{
				this.mainCamera.transform.Translate(Vector3.left * speed * Time.deltaTime);
			}
			if (Input.GetKey(KeyCode.D))
			{
				this.mainCamera.transform.Translate(Vector3.right * speed * Time.deltaTime);
			}
        }
	}

	// Token: 0x0600002A RID: 42 RVA: 0x00003E3C File Offset: 0x0000203C
	private void Jump()
	{
		this.isJumping = true;
		this.rb.velocity = Vector2.up * this.jumpForce;
	}

	// Token: 0x0600002B RID: 43 RVA: 0x00003E60 File Offset: 0x00002060
	private void GeneratePlatform()
	{
		this.lastPlatformPosition = new Vector3(this.lastPlatformPosition.x, this.lastPlatformPosition.y + 200f, this.lastPlatformPosition.z);
		Object.Instantiate<GameObject>(this.platform, this.lastPlatformPosition, Quaternion.identity);
	}

	// Token: 0x0600002C RID: 44 RVA: 0x00003EB8 File Offset: 0x000020B8
	private void showFloatingText(string message, int font = 300)
	{
		GameObject gameObject = Object.Instantiate<GameObject>(this.messageText, new Vector3(base.transform.position.x + -335f, base.transform.position.y + 250f, base.transform.position.z), Quaternion.identity);
		gameObject.GetComponent<TextMesh>().fontSize = font;
		gameObject.GetComponent<TextMesh>().text = message;
	}

	// Token: 0x04000006 RID: 6
	private Rigidbody2D rb;

	// Token: 0x04000007 RID: 7
	public float jumpForce;

	// Token: 0x04000008 RID: 8
	public GameObject platform;

	// Token: 0x04000009 RID: 9
	private Camera mainCamera;

	// Token: 0x0400000A RID: 10
	private Vector3 lastPlatformPosition;

	// Token: 0x0400000B RID: 11
	private List<string> messages;

	// Token: 0x0400000C RID: 12
	public GameObject messageText;

	// Token: 0x0400000D RID: 13
	private bool isJumping;
}
