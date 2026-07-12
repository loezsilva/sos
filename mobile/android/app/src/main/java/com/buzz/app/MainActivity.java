package com.buzz.app;

import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.content.Intent;
import android.media.AudioAttributes;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import com.getcapacitor.BridgeActivity;

public class MainActivity extends BridgeActivity {

    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        criarCanalBuzina();
        processarIntentBuzina(getIntent());
    }

    @Override
    protected void onNewIntent(Intent intent) {
        super.onNewIntent(intent);
        setIntent(intent);
        processarIntentBuzina(intent);
    }

    private void criarCanalBuzina() {
        if (Build.VERSION.SDK_INT < Build.VERSION_CODES.O) {
            return;
        }

        NotificationChannel canal = new NotificationChannel(
            "buzz_chamada",
            "Chamadas Buzz",
            NotificationManager.IMPORTANCE_HIGH
        );
        canal.setDescription("Cutucões urgentes do Cutuca");
        canal.enableVibration(true);
        canal.setVibrationPattern(new long[] { 0, 200, 100, 200, 100, 400 });
        canal.setLockscreenVisibility(android.app.Notification.VISIBILITY_PUBLIC);

        // Assinatura oficial (alias buzina.wav = cutuca_recebido)
        Uri som = Uri.parse("android.resource://" + getPackageName() + "/" + R.raw.buzina);
        AudioAttributes attrs = new AudioAttributes.Builder()
            .setUsage(AudioAttributes.USAGE_NOTIFICATION_RINGTONE)
            .setContentType(AudioAttributes.CONTENT_TYPE_SONIFICATION)
            .build();
        canal.setSound(som, attrs);

        NotificationManager gerenciador = getSystemService(NotificationManager.class);
        if (gerenciador != null) {
            gerenciador.createNotificationChannel(canal);
        }
    }

    private void processarIntentBuzina(Intent intent) {
        if (intent == null) {
            return;
        }

        String url = intent.getStringExtra("url");
        String buzinaId = intent.getStringExtra("buzina_id");

        if (buzinaId == null && intent.getData() != null) {
            buzinaId = intent.getData().getQueryParameter("buzina");
            if (buzinaId == null && intent.getData().getPath() != null) {
                String path = intent.getData().getPath();
                if (path.contains("/buzina/")) {
                    buzinaId = path.substring(path.lastIndexOf('/') + 1);
                }
            }
        }

        if (url == null && buzinaId != null) {
            url = "/?buzina=" + buzinaId;
        }

        if (url != null && getBridge() != null && getBridge().getWebView() != null) {
            String base = getBridge().getServerUrl();
            if (base == null || base.isEmpty()) {
                getBridge().getWebView().loadUrl(url);
            } else {
                getBridge().getWebView().loadUrl(base + url);
            }
        }
    }
}
