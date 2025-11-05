#!/usr/bin/env python3
"""
K.4 Transfer Agent - Proposes and executes knowledge transfers
Port: 8702
"""
import os
import json
import time
from datetime import datetime
from flask import Flask, request, jsonify

app = Flask(__name__)
SIMULATION_MODE = os.getenv('SIMULATION_MODE', 'true').lower() == 'true'
APPROVE_TRANSFER = os.getenv('APPROVE_TRANSFER', 'no').lower() == 'yes'

# Simulated transfer proposals
TRANSFER_PROPOSALS = []

@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy', 
        'simulation_mode': SIMULATION_MODE,
        'approve_transfer': APPROVE_TRANSFER
    })

@app.route('/v1/propose', methods=['POST'])
def propose_transfer():
    """Propose knowledge transfer"""
    data = request.get_json()
    
    if SIMULATION_MODE:
        proposal = {
            'proposal_id': f"transfer-{int(time.time())}",
            'source_experience': data.get('experience_id'),
            'target_workspace': data.get('target_workspace', 'anonymized'),
            'transfer_type': data.get('type', 'pattern'),
            'confidence': data.get('confidence', 0.85),
            'expected_impact': data.get('expected_impact', 'medium'),
            'requires_approval': True,
            'status': 'proposed',
            'proposed_at': datetime.utcnow().isoformat(),
            'simulation': True
        }
        
        TRANSFER_PROPOSALS.append(proposal)
        return jsonify({'status': 'proposed', 'proposal': proposal})
    
    return jsonify({'error': 'Live mode not implemented'}), 501

@app.route('/v1/proposals')
def list_proposals():
    """List transfer proposals"""
    status = request.args.get('status')
    
    if SIMULATION_MODE:
        if status:
            proposals = [p for p in TRANSFER_PROPOSALS if p['status'] == status]
        else:
            proposals = TRANSFER_PROPOSALS
        
        return jsonify({
            'proposals': proposals,
            'total': len(proposals),
            'simulation': True
        })
    
    return jsonify({'proposals': []})

@app.route('/v1/proposals/<proposal_id>/approve', methods=['POST'])
def approve_proposal(proposal_id):
    """Approve transfer proposal"""
    if SIMULATION_MODE:
        proposal = next((p for p in TRANSFER_PROPOSALS if p['proposal_id'] == proposal_id), None)
        if not proposal:
            return jsonify({'error': 'Proposal not found'}), 404
        
        if APPROVE_TRANSFER:
            proposal['status'] = 'approved'
            proposal['approved_at'] = datetime.utcnow().isoformat()
            return jsonify({'status': 'approved', 'proposal': proposal})
        else:
            return jsonify({
                'status': 'simulation_only',
                'message': 'Set APPROVE_TRANSFER=yes for live approval',
                'simulation': True
            })
    
    return jsonify({'error': 'Live mode not implemented'}), 501

@app.route('/v1/execute', methods=['POST'])
def execute_transfer():
    """Execute approved transfer"""
    data = request.get_json()
    proposal_id = data.get('proposal_id')
    
    if SIMULATION_MODE:
        if not APPROVE_TRANSFER:
            return jsonify({
                'status': 'simulation_only',
                'message': 'Transfer execution requires APPROVE_TRANSFER=yes',
                'simulation': True
            })
        
        execution = {
            'execution_id': f"exec-{int(time.time())}",
            'proposal_id': proposal_id,
            'status': 'completed',
            'executed_at': datetime.utcnow().isoformat(),
            'duration_seconds': 30,
            'success': True,
            'simulation': True
        }
        
        return jsonify({'status': 'executed', 'execution': execution})
    
    return jsonify({'error': 'Live mode not implemented'}), 501

@app.route('/v1/audit')
def get_audit_log():
    """Get transfer audit log"""
    if SIMULATION_MODE:
        audit_log = {
            'transfers': len(TRANSFER_PROPOSALS),
            'approved': len([p for p in TRANSFER_PROPOSALS if p.get('status') == 'approved']),
            'executed': 0 if not APPROVE_TRANSFER else 1,
            'simulation': True
        }
        
        return jsonify(audit_log)
    
    return jsonify({'transfers': 0})

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8702))
    app.run(host='0.0.0.0', port=port, debug=SIMULATION_MODE)