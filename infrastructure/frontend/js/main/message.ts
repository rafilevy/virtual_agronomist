export type message = {
    from: boolean,
    time: Date,
    text: string,
    options?: [string],
    status?: boolean,
    canReport?: boolean,
}