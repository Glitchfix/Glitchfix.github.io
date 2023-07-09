---
title: "IPC: Shared memory"
date: 2023-04-20T12:14:34+05:30
description: "concepts of C in Golang"
author: "Shivanjan Chakarvorty"
type: "post"
---

Before we get started let's get an insight on why IPC is needed. Inter Process Communication allows us to exchange information among two or more processes. This is important keep modularity intact.
The communication between two processes can be established via two methods:
1. Message Passing
2. Shared memory

In message passing you can communicate with processes using message queues, sockets or remote procedural calls. It's all fun and games unless you require real time speed.

In shared memory, processes can share a common memory space that can be read from or write onto. This also reduces the number of read write operations in the communication. The OS provides system calls that allow us to manipulate the common memory space.

The way to do it is different in OS.

The **POSIX** way of doing it is using **mmap** but in **System V** we can attach using *shmat*. Although the **System V** API is more easy to implement the **POSIX** compliance is more widely used which can make your code run almost everywhere.

Don't worry we will try all of them.

### Using System V Shared Memory API:

```go
package main

import (
    "fmt"
    "syscall"
)

const SHMSIZE = 1024

func main() {
    // Create a shared memory segment
    shmid, err := syscall.Shmget(syscall.KEY_IPC_PRIVATE, SHMSIZE, 0666|syscall.IPC_CREAT)
    if err != nil {
        fmt.Println(err)
        return
    }

    // Attach to the shared memory segment
    shmptr, err := syscall.Shmat(shmid, 0, 0)
    if err != nil {
        fmt.Println(err)
        return
    }

    // Write to the shared memory segment
    message := []byte("Hello from process 1!")
    copy(shmptr, message)

    // Detach from the shared memory segment
    err = syscall.Shmdt(shmptr)
    if err != nil {
        fmt.Println(err)
        return
    }
}
```

### Using System V Shared Memory API:
```go
package main

import (
    "fmt"
    "os"
    "syscall"
)

func main() {
    // Create a key to identify the shared memory segment
    key := 1234

    // Create the shared memory segment with a size of 4096 bytes
    shmid, err := syscall.Shmget(key, 4096, 0666|syscall.IPC_CREAT)
    if err != nil {
        fmt.Println("Error creating shared memory segment:", err)
        os.Exit(1)
    }

    // Attach to the shared memory segment
    data, err := syscall.Shmat(shmid, nil, 0)
    if err != nil {
        fmt.Println("Error attaching to shared memory segment:", err)
        os.Exit(1)
    }

    // Write a string to the shared memory segment
    message := "Hello, World!"
    copy(data, []byte(message))

    // Detach from the shared memory segment
    err = syscall.Shmdt(data)
    if err != nil {
        fmt.Println("Error detaching from shared memory segment:", err)
        os.Exit(1)
    }

    // Display the message read from the shared memory segment
    fmt.Println("Message read from shared memory segment:", string(data))
}
```

### Using POSIX Shared Memory API:

```go
package main

import (
    "fmt"
    "os"
    "syscall"
)

const SHMSIZE = 1024

func main() {
    // Create a shared memory segment
    shmid, err := syscall.ShmOpen("/myshm", os.O_RDWR|os.O_CREATE|os.O_TRUNC, 0666)
    if err != nil {
        fmt.Println(err)
        return
    }

    // Map the shared memory segment to the process's address space
    shmptr, err := syscall.Mmap(int(shmid), 0, SHMSIZE, syscall.PROT_READ|syscall.PROT_WRITE, syscall.MAP_SHARED)
    if err != nil {
        fmt.Println(err)
        return
    }

    // Write to the shared memory segment
    message := []byte("Hello from process 1!")
    copy(shmptr, message)

    // Unmap the shared memory segment
    err = syscall.Munmap(shmptr)
    if err != nil {
        fmt.Println(err)
        return
    }

    // Close the shared memory segment
    err = syscall.Close(int(shmid))
    if err != nil {
        fmt.Println(err)
        return
    }
}
```