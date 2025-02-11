const { Client, LocalAuth } = require('whatsapp-web.js');
const express = require('express');
const cors = require('cors');
const qrcode = require('qrcode');

const app = express();

app.use(cors());

// If you want to allow only specific origins (e.g., your frontend)

const port = 3000;

const clients = {};

app.use(express.json());

app.get('/health', (req, res) => {
    res.status(200).send('Server is healthy');
});

let qrCodes = {};  // Store QR code URLs in memory

app.post('/start-session', async (req, res) => {
    try {
        console.log("loging in whatsap")
        const { userId } = req.body;

        // Check if the user already has a session
        if (clients[userId]) {
            // Return the stored QR code URL if the session already exists
            const existingQrCode = qrCodes[userId];
            if (existingQrCode) {
                return res.json({ qrCode: existingQrCode });  // Serve the QR code stored in memory
            } else {
                return res.status(400).json({ message: 'Sesión ya iniciada para este usuario' });
            }
        }

        // Initialize a new client for this user
        const client = new Client({
            authStrategy: new LocalAuth({ 
                clientId: userId,
                dataPath: '/home/appuser/app/session-data'  // Custom directory for session storage
            }),
            puppeteer: {
                args: ['--no-sandbox', '--disable-setuid-sandbox'],
                executablePath: process.env.PUPPETEER_EXECUTABLE_PATH || '/usr/bin/chromium',
            },
        });

        clients[userId] = { client, ready: false };

        let qrSent = false;

        // Listen for QR code generation
        client.on('qr', (qr) => {
            if (!qrSent) {
                console.log('QR code generated:', qr);
                qrcode.toDataURL(qr, (err, url) => {
                    if (err) {
                        console.error('Error generating QR code:', err);
                        return res.status(500).json({ message: 'Error generating QR code' });
                    }
                    console.log('QR code URL:', url);
                    qrCodes[userId] = url; // Store the QR code URL for later use
                    res.json({ qrCode: url });
                    qrSent = true;
                });
            }
        });

        // Listen for client readiness
        client.on('ready', () => {
            console.log(`Cliente ${userId} listo`);
            clients[userId].ready = true;
        });

        // Listen for client disconnection
        client.on('disconnected', (reason) => {
            console.log(`Cliente ${userId} desconectado: ${reason}`);
            delete clients[userId];
            delete qrCodes[userId];  // Remove the QR code from memory when the session ends
        });

        // Listen for incoming messages
        client.on('message', async (msg) => {
            console.log(`Mensaje recibido: ${msg.body} de ${msg.from}`);
            if (msg.body.toLowerCase() === 'hola') {
                await msg.reply('¡Hola! ¿Cómo puedo ayudarte?');
            }
        });

        // Initialize the client
        client.initialize().then(() => {
            console.log('Client initialized');
        }).catch((error) => {
            console.error('Error initializing client:', error);
        });
    } catch (error) {
        console.error('Error en el manejo de la sesión:', error);
        res.status(500).json({ message: 'Error en el servidor' });
    }
});



// Endpoint to send a message
app.post('/send-message', async (req, res) => {
    try {
        const { userId, to, message } = req.body;
        console.log(userId)
        console.log(to)
        console.log(message)

        console.log("Clients Object:", clients); // Debug: Print all active clients
        console.log("Received userId:", userId); // Debug: Print received userId

        if (!clients[userId] || !clients[userId].ready) {
            return res.status(400).json({ message: 'Sesión no iniciada o no lista' });
        }

        const client = clients[userId].client;
        const chatId = to.includes('@') ? to : `${to}@c.us`; // Ensure the chat ID is in the correct format
        await client.sendMessage(chatId, message);

        res.status(200).json({ message: 'Mensaje enviado correctamente' });
    } catch (error) {
        console.error('Error enviando mensaje:', error);
        res.status(500).json({ message: 'Error enviando mensaje' });
    }
});

// Endpoint to fetch all chats
app.get('/get-chats', async (req, res) => {
    try {
        const { userId } = req.query;

        if (!clients[userId] || !clients[userId].ready) {
            return res.status(400).json({ message: 'Sesión no iniciada o no lista' });
        }

        const client = clients[userId].client;
        const chats = await client.getChats();

        res.status(200).json({ chats: chats.map(chat => ({ id: chat.id._serialized, name: chat.name })) });
    } catch (error) {
        console.error('Error obteniendo chats:', error);
        res.status(500).json({ message: 'Error obteniendo chats' });
    }
});

// Endpoint to fetch messages from a specific chat
app.get('/get-messages', async (req, res) => {
    try {
        const { userId, chatId } = req.query;

        if (!clients[userId] || !clients[userId].ready) {
            return res.status(400).json({ message: 'Sesión no iniciada o no lista' });
        }

        const client = clients[userId].client;
        const chat = await client.getChatById(chatId);
        const messages = await chat.fetchMessages({ limit: 50 }); // Fetch last 50 messages

        res.status(200).json({ messages: messages.map(msg => ({
            id: msg.id._serialized,
            from: msg.from,
            body: msg.body,
            timestamp: msg.timestamp
        })) });
    } catch (error) {
        console.error('Error obteniendo mensajes:', error);
        res.status(500).json({ message: 'Error obteniendo mensajes' });
    }
});

// Endpoint to log out and end a session
app.post('/logout', async (req, res) => {
    try {
        const { userId } = req.body;

        if (!clients[userId]) {
            return res.status(400).json({ message: 'Sesión no iniciada' });
        }

        const client = clients[userId].client;
        await client.logout();
        delete clients[userId];

        res.status(200).json({ message: 'Sesión cerrada correctamente' });
    } catch (error) {
        console.error('Error cerrando sesión:', error);
        res.status(500).json({ message: 'Error cerrando sesión' });
    }
});

// Endpoint to check if a session is ready
app.get('/session-status', async (req, res) => {
    try {
        const { userId } = req.query;

        if (!clients[userId]) {
            return res.status(400).json({ message: 'Sesión no iniciada' });
        }

        res.status(200).json({ ready: clients[userId].ready });
    } catch (error) {
        console.error('Error verificando estado de sesión:', error);
        res.status(500).json({ message: 'Error verificando estado de sesión' });
    }
});


// Endpoint to verify the session
app.get('/verify-session', async (req, res) => {
    try {
        const { userId } = req.query;

        // Check if the session is ready
        if (!clients[userId] || !clients[userId].ready) {
            return res.status(400).json({ message: 'La sesión no está lista o no iniciada' });
        }

        // Session is verified, return success message
        res.status(200).json({ message: `Sesión verificada con éxito para el usuario ${userId}` });
    } catch (error) {
        console.error('Error verificando la sesión:', error);
        res.status(500).json({ message: 'Error verificando la sesión' });
    }
});





// Add other routes (get-chats, get-messages, send-message, etc.) here...

app.listen(port, '0.0.0.0', () => {
    console.log(`Servidor de WhatsApp corriendo en http://localhost:${port}`);
});