import {runInAction} from 'mobx'
import {AaaSession, localStorageAuthorizationKeyname, AaaAuthorizationSession} from "../types/aaa";
import {aaaProvider} from "./provider";
import {ClientSessionResponse, session} from './session'
import {request, updateAuthorizationHeader} from 'system/requests'


export type AaaInterface = {
  initializeFromServer(): Promise<any>
  initializeFromStruct(authsession: ClientSessionResponse): void
  dropSession(): void
  getAuthorizationSession(): AaaSession
  storeAuthorizationSession(session: AaaSession): void
  dropAuthorizationSession(): void
  getAuthorizationToken(): string | null
  getRefreshToken(): string | null
  authenticate(username: string, password: string): Promise<AaaSession>
  logout(): void
  isLoggedIn(): boolean
  check(): Promise<any>
}


export const aaa: AaaInterface = {
  async initializeFromServer() {
    await aaaProvider.touch().then(res => {
      const authsession: ClientSessionResponse = res.data
      aaa.initializeFromStruct(authsession)
    }).catch(() => {
      aaa.dropSession()
    })
  },

  initializeFromStruct(authsession: ClientSessionResponse) {
    runInAction(() => {
      session.user = authsession?.user || null
      session.permissions = authsession?.permissions || []
      if (authsession === null || authsession?.user === null) {
        aaa.dropAuthorizationSession()
      }
    })
  },

  dropSession() {
    runInAction(() => {
      session.user = null
      session.permissions = []
      aaa.dropAuthorizationSession()
    })
  },

  getAuthorizationSession(): AaaSession {
    const storedSession: string | null = localStorage.getItem(localStorageAuthorizationKeyname)
    if (storedSession === null)
      return null
    return JSON.parse(storedSession)
  },

  storeAuthorizationSession(session: AaaSession): void {
    localStorage.setItem(localStorageAuthorizationKeyname, JSON.stringify(session))
  },

  dropAuthorizationSession(): void {
    localStorage.removeItem(localStorageAuthorizationKeyname)
  },

  getAuthorizationToken(): string | null {
    const session: AaaSession = aaa.getAuthorizationSession()
    if (session === null)
      return null
    const token: string = String(session.token)
    return `Bearer ${token}`
  },

  getRefreshToken(): string | null {
    const session: AaaSession = aaa.getAuthorizationSession()
    if (session === null)
      return null
    return String(session.refreshToken)
  },

  async authenticate(username: string, password: string): Promise<AaaSession> {
    return await aaaProvider.login(username, password).then(response => {
      const authorizationSession: AaaAuthorizationSession = response.data
      aaa.storeAuthorizationSession(authorizationSession)
      updateAuthorizationHeader(aaa.getAuthorizationToken())
      return authorizationSession
    })
  },

  logout() {
    runInAction(() => {
      aaa.dropAuthorizationSession()
      session.user = null
      session.permissions = []
      updateAuthorizationHeader(null)
    })
  },

  isLoggedIn() {
    return session.user !== null
  },

  check() {
    return aaaProvider.check()
  }
}
