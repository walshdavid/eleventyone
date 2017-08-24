///////////////////////////////////////////////////////////////
//                  Video images                             //
///////////////////////////////////////////////////////////////
/*
imports the socket io libary and opens port 1235 to list
for incoming connections
*/
var io = require('socket.io').listen(1235);
//required to write files
var fs = require('fs');
var counter = 1;
/* 
    catches each client connection and
    handles the communication messages
*/
io.sockets.on('connection', function (socket) {
    //prints server side only
    console.log("a new user has connected");
    socket.on("start", function (data) {
        console.log(data);
    });
    socket.on("videoimages", function (vid, name) {
        //send vid to all clients testing only
        //socket.broadcast.emit('stream', vid);
        // console.log(vid);
        var imageBuffer = decodeBase64Image(vid);
        if (imageBuffer != "null") {
            fs.writeFile(name, imageBuffer.data, function (err) {
                console.log(err);
            });
            console.log(imageBuffer);
        }
    });
    //////////////////////////////////////////////////
    //when a user disconnects
    socket.on('disconnect', function () {
        //prints server side only
        console.log("user disconnected");
    });
}); // end off socket code
//base 64 image convertor
function decodeBase64Image(dataString) {
    var matches = dataString.match(/^data:([A-Za-z-+\/]+);base64,(.+)$/)
        , response = {};
    if (matches.length !== 3) {
        return new Error('Invalid input string');
    }
    response.type = matches[1];
    response.data = new Buffer(matches[2], 'base64');
    return response;
}
///////////////////////////////////////////////////////////////
//                         Audio                             //
///////////////////////////////////////////////////////////////
//this app is only for websockets and will not serve webpages
var BinaryServer = require('binaryjs').BinaryServer;
//required for file format
var wav = require('wav');
console.log('server started');
//creates a websocked binary server
var server = BinaryServer({
    port: 9000
});
//listens for audio stream connection
server.on('connection', function (client) {
    console.log('new connection');
    //used to ensure the fiel is only created once
    var nameset = true;
    console.log(nameset);
    //when the stream is recieved
    client.on('stream', function (stream, meta) {
        //checks if the name is set 
        if (nameset) {
            //creates a new file, with file type & file location and file name used the meta recieved
            var fileWriter = new wav.FileWriter(meta, {
                //sets the file sets 
                channels: 1
                , sampleRate: 44100
                , bitDepth: 16
            });
            //sets the nameset to false so the fileWriter is not recreated everytime data is recieved
            nameset = false;
        }
        console.log('stream started');
        //adds the streamed content to the fileWriter using a pip
        stream.pipe(fileWriter);
        //when the streamed audio ends
        stream.on('end', function () {
            //creted the file by closing the file writer
            fileWriter.end();
            console.log('new file created');
        });
    });
});