# LanChat
Local Area Network - Messaging application in CLI with Python Sockets

## Description
A Local Area Network based Text messaging application in a Command-Line Interface . The whole application is developed in python aimed at using in a windows enviornment using Standard Libraries which include :

* Sockets
* Threading
* Os
* Sys
* Random
* Time
* Msvcrt

**The application does not work in a linux since it does not have msvcrt**

This is not a Refined Application , So more refined and controllable ones will be released in the future.

## Main Features
* Service auto Discovery
* Auto Disconnection in Forced exits from client side
* Colored and Responsive than Normal CLI

## Usage

The Server will handle itself after you start running it. After a server is actively running in lan in any IP the client can discover the service automatically and connect to it. If there are no services found running the client will stop. Otherwise it Prompts you with a Username Section to choose a name and a chat specific color for your username will be given. After that you can pretty much text in anything. To disconnect you can use any of the prefined Commands.

## Commands

* ! DISCONNECT ! -> Disconnects you from the server and exits the application
* exit           -> Same as the disconnect but easy to type.
* !SHUTDOWN!     -> Shutdown will be initiated from the Client-side(Probably not a good Idea So as I said not so Refined)



