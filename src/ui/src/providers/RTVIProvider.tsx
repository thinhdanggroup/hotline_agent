import { type PropsWithChildren } from 'react';
import { RTVIClient } from '@pipecat-ai/client-js';
import { DailyTransport } from '@pipecat-ai/daily-transport';
import { RTVIClientProvider } from '@pipecat-ai/client-react';

const transport = new DailyTransport();

const client = new RTVIClient({
  transport,
  params: {
    baseUrl: import.meta.env.VITE_API_URL,
    endpoints: {
      connect: '/connect',
    },
  },
  enableMic: true,
  enableCam: false,
});

export function RTVIProvider({ children }: PropsWithChildren) {
  return <RTVIClientProvider client={client}>{children}</RTVIClientProvider>;
}
