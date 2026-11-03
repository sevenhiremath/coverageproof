"""Bounded hosted inference. Credentials and provider error bodies are never logged."""
import json
import os
import time
from hashlib import sha256
import httpx
from .domain import now


class GroqProvider:
    def structured(self, schema, system_prompt, context):
        self.raw_output = b''
        self.trace = {'provider':'groq', 'started':now(), 'output_complete':False}
        started = time.monotonic()
        try:
            key = os.environ.get('GROQ_API_KEY', '').strip()
            if not key:
                raise ValueError('GROQ_API_KEY is not configured')
            model = os.environ.get('GROQ_MODEL', 'openai/gpt-oss-120b')
            self.trace['requested_model'] = model
            payload = {'model':model, 'stream':False, 'temperature':0, 'max_completion_tokens':2048,
                'messages':[{'role':'system','content':system_prompt}, {'role':'user','content':json.dumps(context)}],
                'response_format':{'type':'json_schema','json_schema':{'name':'coverageproof_response','strict':False,'schema':schema}}}
            raw = bytearray()
            with httpx.Client(timeout=60, trust_env=False, follow_redirects=False) as client:
                with client.stream('POST', 'https://api.groq.com/openai/v1/chat/completions',
                        headers={'Authorization':'Bearer ' + key}, json=payload) as response:
                    self.trace['http_status'] = response.status_code
                    if response.status_code != 200:
                        raise ValueError(f'Groq returned HTTP {response.status_code}; no retry or fallback was substituted')
                    for chunk in response.iter_bytes():
                        if len(raw) + len(chunk) > 262144:
                            raise ValueError('Groq response exceeded 256 KiB')
                        raw.extend(chunk)
            result = json.loads(raw)
            choice = result['choices'][0]
            content = choice['message']['content']
            if not isinstance(content, str):
                raise ValueError('Groq returned no text response')
            self.raw_output = content.encode()
            self.trace['output_complete'] = choice.get('finish_reason') == 'stop'
            self.trace['finish_reason'] = str(choice.get('finish_reason'))[:80]
            if not self.trace['output_complete']:
                raise ValueError('Groq response was incomplete')
            return content
        except httpx.HTTPError as error:
            self.trace['error_type'] = type(error).__name__
            raise ValueError('Groq request failed: ' + type(error).__name__) from None
        except (KeyError, IndexError, TypeError, AttributeError, json.JSONDecodeError):
            raise ValueError('Groq returned an unsupported response shape') from None
        finally:
            self.trace['elapsed_ms'] = round((time.monotonic()-started)*1000, 3)
            self.trace['output_size'] = len(self.raw_output)
            self.trace['output_sha256'] = sha256(self.raw_output).hexdigest() if self.raw_output else None

    def propose(self, snapshot):
        from .planner import Proposal, model_plan_schema, SYSTEM_PROMPT, model_context
        proposal = Proposal.model_validate_json(self.structured(model_plan_schema(snapshot), SYSTEM_PROMPT, model_context(snapshot)))
        if proposal.mode != 'model':
            raise ValueError('Groq returned invalid reasoning provenance')
        return proposal
