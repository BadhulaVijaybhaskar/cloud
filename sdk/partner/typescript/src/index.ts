// minimal client
import fetch from "node-fetch";

export class AtomPartnerClient {
  base: string;
  token?: string;
  constructor(base = process.env.ATOM_PARTNER_BASE || "http://localhost:8200", token?: string) {
    this.base = base;
    this.token = token;
  }
  async registerPartner(payload: any) {
    const res = await fetch(`${this.base}/v1/partners`, {
      method: "POST", headers: {"content-type":"application/json"}, body: JSON.stringify(payload)
    });
    return res.json();
  }
}