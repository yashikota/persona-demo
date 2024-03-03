using UnityEngine;
using OscJack;

public class OSC : MonoBehaviour
{
    [SerializeField] private int port = 5005;
    private OscServer server;

    // Start is called before the first frame update
    void Start()
    {
        server = new OscServer(port);
        server.MessageDispatcher.AddCallback(
            "/image",
            (string address, OscDataHandle data) =>
            {
                Debug.Log("Data: " + data.GetElementAsString(0));
            }
        );
    }

    // Update is called once per frame
    void Update()
    {

    }

    private void OnDestroy()
    {
        server.Dispose();
        server = null;
    }
}
